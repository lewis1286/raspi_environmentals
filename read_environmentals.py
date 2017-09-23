#! /usr/bin/python -p
'''
This runs in background constantly on systemctl.  make it a permanent
while True loop

systemctl file found at:
    /lib/systemd/service/environmental.serivce
    remember to chmod 664 the service if making a new one
    see https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/System_Administrators_Guide/sect-Managing_Services_with_systemd-Unit_Files.html#sect-Managing_Services_with_systemd-Unit_File_Create
    and https://stackoverflow.com/questions/13069634/python-daemon-and-systemd-service

when making changes to this file, be sure to do:
    sudo systemctl daemon-reload
    sudo systemctl restart environmental.service
'''

import smbus
import time
from sense_hat import SenseHat
import pickle
import time
import os
import datetime

sense = SenseHat()

def mpl():
    '''
    Read environmentals from MPL3115A2 and return as dictionary
    adapted from: https://www.controleverything.com/products
    outputs:
        dict()
    '''
    # Get I2C bus
    bus = smbus.SMBus(1)

    # MPL3115A2 address, 0x60(96)
    # Select control register, 0x26(38)
    #		0xB9(185)	Active mode, OSR = 128, Altimeter mode
    bus.write_byte_data(0x60, 0x26, 0xB9)
    # MPL3115A2 address, 0x60(96)
    # Select data configuration register, 0x13(19)
    #		0x07(07)	Data ready event enabled for altitude, pressure, temperature
    bus.write_byte_data(0x60, 0x13, 0x07)
    # MPL3115A2 address, 0x60(96)
    # Select control register, 0x26(38)
    #		0xB9(185)	Active mode, OSR = 128, Altimeter mode
    bus.write_byte_data(0x60, 0x26, 0xB9)

    time.sleep(1)

    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 6 bytes
    # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
    data = bus.read_i2c_block_data(0x60, 0x00, 6)

    # Convert the data to 20-bits
    tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    temp = ((data[4] * 256) + (data[5] & 0xF0)) / 16
    altitude = tHeight / 16.0
    cTemp = temp / 16.0
    fTemp = cTemp * 1.8 + 32

    # MPL3115A2 address, 0x60(96)
    # Select control register, 0x26(38)
    #		0x39(57)	Active mode, OSR = 128, Barometer mode
    bus.write_byte_data(0x60, 0x26, 0x39)

    time.sleep(1)

    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 4 bytes
    # status, pres MSB1, pres MSB, pres LSB
    data = bus.read_i2c_block_data(0x60, 0x00, 4)

    # Convert the data to 20-bits
    pres = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    pressure = (pres / 4.0) / 1000.0 # kilopascal

    # Output data to screen
    # print "Pressure : %.2f kPa" %pressure
    # print "Altitude : %.2f m" %altitude
    # print "Temperature in Celsius  : %.2f C" %cTemp
    # print "Temperature in Fahrenheit  : %.2f F" %fTemp
    return dict(mplTemp=fTemp,
                mplPressure=pressure,
                mplAltitude=altitude)

# main loop
while True:
    all_data = []     # do 2 hours per file, one reading every 10 seconds
    for _ in range(720):

        t = sense.get_temperature() # degrees C
        p = sense.get_pressure() # millibar
        h = sense.get_humidity() # pct relative humidity

        # conversions
        t = (t * 1.8) + 32 # make farenheit .. will need to calibrate too
        p /= 10 # convert to kPa

        t = round(t, 1)
        p = round(p, 1)
        h = round(h, 1)
        data = {}
        data['shTemp'] = str(t).encode('utf-8')
        data['shPres'] = str(p).encode('utf-8')
        data['shHum'] = str(h).encode('utf-8')
        data['Timestamp'] = str(datetime.datetime.now()).encode('utf-8')
        data.update(mpl()) # add mpl11582 data
        all_data.append(data)
        time.sleep(10)
    filename = str(time.time()).split('.')[0] + '_data.p'
    pickle.dump(all_data, open('data/' + filename, 'wb'))
    os.system('scp -i /home/pi/lewis-key-pair-oregon-wp.pem /home/pi/environmentals/data/' + filename + ' ubuntu@54.68.40.151:/home/ubuntu/environmentals/data/')

