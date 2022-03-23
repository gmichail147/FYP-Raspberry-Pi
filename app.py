#!/usr/bin/python

from flask import Flask, jsonify, redirect, render_template, url_for, request

import sqlite3
import logging

from bme280 import BME280
from enviroplus import gas
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from time import sleep, time, asctime, localtime, strftime, gmtime
from math import ceil, floor
import sqlite3
import json
import os

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

bus = SMBus(1)

bme280 = BME280(i2c_dev=bus) # BME280 temperature, humidity and pressure sensor


pms5003 = PMS5003() # PMS5003 particulate sensor


conn=sqlite3.connect('sensorReadings.db', check_same_thread=False)
curs=conn.cursor()

# Retrieve data from database
def getData():
    
    for row in curs.execute("SELECT * FROM enviro ORDER BY timestamp DESC LIMIT 1"):
        time = str(row[0])
        temp = row[1]
        hum = row[2]
        pres = row[3]
        light = row[4]
        oxid = row[5]
        red = row[6]
        nh3 = row[7]
        pm1 = row[8]
        pm25 = row[9]
        pm10 = row[10]
        
    #conn.close()
    return time, temp, hum, pres, light, oxid, red, nh3, pm1, pm25, pm10


# def get_sensor_data():
    # data = {} #create a dictionary for the data
    # data['humidity'] = bme280.get_humidity()
    # data['pressure'] = bme280.get_pressure()
    # data['temperature'] = bme280.get_temperature()
    # data['light'] = ltr559.get_lux()
    # gases = gas.read_all()
    # data['oxidising'] = round(gases.oxidising / 1000, 1)
    # data['reducing'] = round(gases.reducing / 1000)
    # data['nh3'] = round(gases.nh3 / 1000)
    
    # particles = pms5003.read()

    # data['pm1'] = float(particles.pm_ug_per_m3(1.0))
    # data['pm25'] = float(particles.pm_ug_per_m3(2.5))
    # data['pm10'] = float(particles.pm_ug_per_m3(10))
    
    # return data
    



app = Flask(__name__)

@app.route('/')
def index():
    time, temp, hum, pres, light, oxid, red, nh3, pm1, pm25, pm10 = getData()
    
    templateData = {
        'time': time,
        'temp': temp,
        'hum': hum,
        'pres': pres,
        'light': light,
        'oxid': oxid,
        'red': red,
        'nh3': nh3,
        'pm1': pm1,
        'pm25': pm25,
        'pm10': pm10
    }
    
    return render_template('index.html', **templateData)

@app.route('/camera')
def camera():
    
    return render_template('camera.html')





if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0')


