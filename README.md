# Read environmental information and plot with bokeh

There are two main files:

## read_environmentals.py
This file reads environmental information from the raspberry pi sense-hat as
well as the MPL3115A2 sensors (for calibration), saves them, and then pushes
them to an AWS EC2 instance which in turn plots them.
There is another directory to be created in the home directory '~/data' where
the files will be saved locally.

## environmentals.py
This file lives on the EC2 instance and plots the data from the raspberry pi on
a bokeh server.  There is another directory '~/data' that needs to be created
in the home directory for storing the data.
