import numpy as np
import pandas as pd
from bokeh.plotting import figure, curdoc
from bokeh.embed import components, server_document
from bokeh.models.sources import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.layouts import column, layout
from bokeh.models import Legend, Range1d
import os
from os import listdir
import sqlite3
# test text
# --------------  Extract  -----------------------
def get_data():
    path = '/home/ubuntu/data/'
    pickle_names = listdir(path)
    # don't read in the sqlite db
    pickle_names = [x for x in pickle_names if x.split('.')[1] == 'p']

    df = pd.DataFrame()
    for pickle_name in pickle_names:
        df = pd.concat([df, pd.DataFrame(pd.read_pickle(path + pickle_name))])


    # here we update our sqlite database and then cleanup the datafiles in the
    # directory
    conn = sqlite3.connect(path + 'environmentals.db')
    # write new records to sql table
    df.to_sql('raw', conn, if_exists='append')
    # now read all records from sql table
    df = pd.read_sql_query('select * from raw', conn)
    conn.close()
    # clean up pickle files from data directory
    for name in pickle_names:
        os.remove(path + name)

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
CIRCLE_ARGS=dict(
            size=15,
            alpha=.01,
            hover_alpha=0.3,
            line_color=None,
            hover_line_color='white',
        )
LINE_ARGS=dict(
            line_width=3,
            line_dash='4 4'
        )
temp = figure(title='Temperature (F)',
            **FIG_ARGS)
shTemp = temp.circle('Timestamp',
                   'shTemp',
                   source=ds_source,
                   color='#885053',
                   **CIRCLE_ARGS)
shTempLine = temp.line('Timestamp',
            'shTemp',
            source=ds_source,
            color='#885053',
            **LINE_ARGS)
mplTemp = temp.circle('Timestamp',
                    'mplTemp',
                    source=ds_source,
                    color='#777DA7',
                    **CIRCLE_ARGS)
mplTempLine = temp.line('Timestamp',
                    'mplTemp',
                    source=ds_source,
                    color='#777DA7',
                    **LINE_ARGS)
legend = Legend(items=[
                        ("SenseHat Temp", [shTempLine]),
                        ("MPL3115A2 Temp", [mplTempLine])
                       ],
                location=(0, -60),
                border_line_color=None
                )
temp.add_layout(legend, 'right')
temp.add_tools(HoverTool(tooltips=None,
                         renderers=[shTemp, mplTemp],
                         mode='vline')
                )

# Humidity
hum = figure(title='Humidity (relative %)',
            x_range=temp.x_range,
            **FIG_ARGS)
shHum = hum.circle('Timestamp', 'shHum', source=ds_source,
         color='#C05931',
         size=2)
hum.line('Timestamp', 'shHum', source=ds_source,
         color='#C05931',
         line_width=1)
legend = Legend(items=[("SenseHat Humidity", [shHum])],
                location=(0, -60),
                border_line_color=None
                )
hum.add_layout(legend, 'right')


# Pressure
pres = figure(title='Pressure (kPa)',
            x_range=temp.x_range,
            y_range=Range1d(100, 102),
            **FIG_ARGS)
shPres = pres.circle('Timestamp',
                   'shPres',
                   source=ds_source,
                   color='#474842')
pres.line('Timestamp',
                   'shPres',
                   source=ds_source,
                   line_width=1,
                   color='#474842')
mplPres = pres.circle('Timestamp',
                    'mplPressure',
                    source=ds_source,
                    color='#748275')
legend = Legend(items=[
                        ("SenseHat Pressure", [shPres]),
                        ("MPL3115A2 Pressure", [mplPres]),
                        ],
                border_line_color=None,
                location=(0, -60))
pres.add_layout(legend, 'right')

# script = server_document(url="http://www.diffusecreation.com:8080/environmentals")
# print(script)

def get_new_data():
    # need to pull in new data and append it to df
    ds_source = get_data()

curdoc().add_root(layout([temp, hum, pres],
                  sizing_mode='stretch_both'))
curdoc().title='environmental sensors'
# get new data every two hours
curdoc().add_periodic_callback(get_new_data, 600000)
