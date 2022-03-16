#!/usr/bin/python

from flask import Flask, jsonify, redirect, render_template
from bme280 import BME280

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus) # BME280 temperature, humidity and pressure sensor

def get_sensor_data():
	data = {} #create a dictinary for the data
	data['humidity'] = bme280.get_humidity()
	data['pressure'] = bme280.get_pressure()
	data['temperature'] = bme280.get_temperature()
	return data


app = Flask(__name__)

@app.route('/')
def index():
	data = get_sensor_data()
	return render_template('index.html', data=sorted(data.items()))

@app.route('/download')
def download():
	return jsonify(get_sensor_data())




if __name__ == '__main__':
	
	app.run(debug=False, host='0.0.0.0')

