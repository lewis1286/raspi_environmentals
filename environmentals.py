import numpy as np
import pandas as pd
from bokeh.plotting import figure, curdoc
from bokeh.embed import components, server_document 
from bokeh.models.sources import ColumnDataSource
from bokeh.layouts import column
from bokeh.models import Legend, Range1d
from os import listdir
# test text
# --------------  Extract  -----------------------
def get_data():
    path = '/home/ubuntu/data/'
    pickle_names = listdir(path)

    df = pd.DataFrame()
    for pickle_name in pickle_names:
        df = pd.concat([df, pd.DataFrame(pd.read_pickle(path + pickle_name))])

    # update datatypes
    df['shTemp'] = df['shTemp'].astype('float')
    df['shHum'] = df['shHum'].astype('float')
    df['shPres'] = df['shPres'].astype('float')
    df['mplTemp'] = df['mplTemp'].astype('float')
    df['mplAltitude'] = df['mplAltitude'].astype('float')
    df['mplPressure'] = df['mplPressure'].astype('float')
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
        background_fill_color='#ECE4B7',
        tools=TOOLS,
        toolbar_location='above'
        )
# Temperature
temp = figure(title='Temperature (F)',
            **FIG_ARGS)
shTemp = temp.line('Timestamp',
                   'shTemp',
                   source=ds_source,
                   color='#885053')
mplTemp = temp.line('Timestamp',
                    'mplTemp',
                    source=ds_source,
                    color='#777DA7')
legend = Legend(items=[
                ("SenseHat Temp", [shTemp]),
                ("MPL3115A2 Temp", [mplTemp])
                ], location=(0, -60))
temp.add_layout(legend, 'right')


# Humidity
hum = figure(title='Humidity (relative %)',
            x_range=temp.x_range,
            **FIG_ARGS)
shHum = hum.line('Timestamp', 'shHum', source=ds_source,
         color='#C05931',
         line_width=2)
legend = Legend(items=[
                ("SenseHat Humidity", [shHum]),
                ], location=(0, -60))
hum.add_layout(legend, 'right')


# Pressure
pres = figure(title='Pressure (kPa)',
            x_range=temp.x_range,
            **FIG_ARGS)
shPres = pres.line('Timestamp',
                   'shPres',
                   source=ds_source,
                   color='#474842')
mplPres = pres.line('Timestamp',
                    'mplPressure',
                    source=ds_source,
                    color='#748275')
legend = Legend(items=[
                ("SenseHat Pressure", [shPres]),
                ("MPL3115A2 Pressure", [mplPres]),
                ], location=(0, -60))
pres.add_layout(legend, 'right')

# script = server_document(url="http://www.diffusecreation.com:8080/environmentals")
# print(script)

def get_new_data():
    # need to pull in new data and append it to df
    ds_source = get_data()

curdoc().add_root(column([temp, hum, pres]))
curdoc().title='environmental sensors'
# get new data every two hours
curdoc().add_periodic_callback(get_new_data, 600000)
