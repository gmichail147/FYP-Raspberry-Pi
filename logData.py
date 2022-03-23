import time
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
    
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""log.py - Reading from all sensors.

Press Ctrl+C to exit!

""")

bus = SMBus(1)

bme280 = BME280(i2c_dev=bus) # BME280 temperature, humidity and pressure sensor


pms5003 = PMS5003() # PMS5003 particulate sensor

dbname='sensorReadings.db'
readFreq = 5 # time in seconds

# get data from DHT sensor
def getSensorData():    
    
    hum = bme280.get_humidity()
    pres = bme280.get_pressure()
    temp = bme280.get_temperature()
    light = ltr559.get_lux()
    
    gases = gas.read_all()
    oxid = round(gases.oxidising / 1000, 1)
    red = round(gases.reducing / 1000)
    nh3 = round(gases.nh3 / 1000)
    
    particles = pms5003.read()

    pm1 = float(particles.pm_ug_per_m3(1.0))
    pm25 = float(particles.pm_ug_per_m3(2.5))
    pm10 = float(particles.pm_ug_per_m3(10))
    
    return temp, hum, pres, light, oxid, red, nh3, pm1, pm25, pm10

# log sensor data on database
def logData (temp, hum, pres, light, oxid, red, nh3, pm1, pm25, pm10):
    
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    
    curs.execute("INSERT INTO enviro values(datetime('now'), (?), (?), (?), (?), (?), (?), (?), (?), (?), (?))", (temp, hum, pres, light, oxid, red, nh3, pm1, pm25, pm10))
    
    conn.commit()
    conn.close()

# main function
def main():
    while True:
        temp, hum, pres, light, oxid, red, nh3, pm1, pm25, pm10 = getSensorData()
        logData (temp, hum, pres, light, oxid, red, nh3, pm1, pm25, pm10)
        logging.info("""
Temperature: {:05.2f} *C
Pressure: {:05.2f} hPa
Relative humidity: {:05.2f} %
Light: {:05.2f} lux
""".format(temp, pres, hum, light))
        time.sleep(readFreq)

# ------------ Execute program 
main()
