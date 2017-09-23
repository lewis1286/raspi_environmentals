import numpy as np
import pandas as pd
from bokeh.plotting import figure, curdoc
from bokeh.embed import components, server_document 
from bokeh.models.sources import ColumnDataSource
from bokeh.layouts import column
from os import listdir
# test text
# --------------  Extract  -----------------------
def get_data():
    path = '/home/ubuntu/environmentals/data/'
    pickle_names = listdir(path)

    df = pd.DataFrame()
    for pickle_name in pickle_names:
        df = pd.concat([df, pd.DataFrame(pd.read_pickle(path + pickle_name))])
    # update datatypes
    df['Temp'] = df['Temp'].astype('float')
    df['Hum'] = df['Hum'].astype('float')
    df['Pres'] = df['Pres'].astype('float')
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values('Timestamp', ascending=True)
    source = ColumnDataSource(df)
    return source

ds_source = get_data()
# ----------   Plotting   -----------------
WIDTH=800
HEIGHT=200
TOOLS = 'pan,box_zoom,wheel_zoom,reset,save'
FIG_ARGS = dict(
        x_axis_type='datetime',
        plot_width=WIDTH,
        plot_height=HEIGHT,
        background_fill_color='#EEE9FA',
        tools=TOOLS
        )
p1 = figure(title='Temperature',
           **FIG_ARGS)
p1.line('Timestamp', 'Temp', source=ds_source,
        color='#505080')

p2 = figure(title='Humidity', x_range=p1.x_range,
            **FIG_ARGS)
p2.line('Timestamp', 'Hum', source=ds_source,
         color='#335C7E',
         line_width=2)

p3 = figure(title='Pressure', x_range=p1.x_range,
            **FIG_ARGS)
p3.line('Timestamp', 'Pres',  source=ds_source,
        color='#2D5D7B')

# script = server_document(url="http://www.diffusecreation.com:8080/environmentals")
# print(script)

def get_new_data():
    # need to pull in new data and append it to df
    ds_source = get_data()
curdoc().add_root(column([p1, p2, p3]))
curdoc().title='environmental sensors'
# get new data every two hours
curdoc().add_periodic_callback(get_new_data, 43200000)
