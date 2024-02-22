# Script to read and write BNO055 IMU data to CSV file
# Author: Pietro Califano
# Date of creation: 03/01/2024
# Derived from Adafruit Python sensor library

import board
import busio
import adafruit_bno055
import time
import csv
import os 
from math import (floor, ceil)

#import sys
#sys.path.append('/home/peterc/devDir/codeRepoPeterC/python/TimersModule.py')
#import TimersModule

# Create BNO sensor connection via I2C
i2c_link = busio.I2C(board.SCL, board.SDA)
BN055sensor = adafruit_bno055.BNO055_I2C(i2c_link)

# Create BNO sensor connection via UART
#BAUDRATE = 115200
#UART_link = serial.Serial("/dev/serial0", BAUDRATE)
#BN055sensor = adafruit_bno055.BNO055_UART(UART_link)

hours2sec = 3600.0
LOG_TIME = ceil(hours2sec * 1) # [hr]
BNO_UPDATE_FREQUENCY_HZ = 1 #Reading frequency
LOGFILE_DIR = ''
LOGGILE_NAME = 'BN055_IMUdata_LOG.csv'

LOGFILE_PATH = os.path.join(LOGFILE_DIR, LOGGILE_NAME)

def readIMUData_BN055(BN055sensor, IMUdata, IMUdataUnits):

    # Read data from BN055sensor instance
    (eulerX, eulerY, eulerZ) = BN055sensor.euler
    IMUdata["eulerX"] = eulerX
    IMUdata["eulerY"] = eulerY
    IMUdata["eulerZ"] = eulerZ

    IMUdataUnits["eulerX"] = 'deg' 
    IMUdataUnits["eulerY"] = 'deg'
    IMUdataUnits["eulerZ"] = 'deg' 

    (lin_accelX, lin_accelY, lin_accelZ) = BN055sensor.linear_acceleration
    IMUdata["lin_accelX"] = lin_accelX
    IMUdata["lin_accelY"] = lin_accelY
    IMUdata["lin_accelZ"] = lin_accelZ

    IMUdataUnits["lin_accelX"] = 'm/s^2' 
    IMUdataUnits["lin_accelY"] = 'm/s^2'
    IMUdataUnits["lin_accelZ"] = 'm/s^2'

    (accelX, accelY, accelZ) = BN055sensor.acceleration
    IMUdata["accelX"] = accelX
    IMUdata["accelY"] = accelY
    IMUdata["accelZ"] = accelZ

    IMUdataUnits["accelX"] = 'm/s^2' 
    IMUdataUnits["accelY"] = 'm/s^2'
    IMUdataUnits["accelZ"] = 'm/s^2'

    (magX, magY, magZ) = BN055sensor.magnetic
    IMUdata["magX"] = magX
    IMUdata["magY"] = magY
    IMUdata["magZ"] = magZ

    IMUdataUnits["magX"] = 'muT' 
    IMUdataUnits["magY"] = 'muT'
    IMUdataUnits["magZ"] = 'muT'

    (gyrosX, gyrosY, gyrosZ) = BN055sensor.gyro
    IMUdata["gyrosX"] = gyrosX
    IMUdata["gyrosY"] = gyrosY
    IMUdata["gyrosZ"] = gyrosZ

    IMUdataUnits["gyrosX"] = 'rad/s' 
    IMUdataUnits["gyrosY"] = 'rad/s'
    IMUdataUnits["gyrosZ"] = 'rad/s'

    #IMUdata["temp"] = BN055sensor.temperature
    #IMUdata["calibration"] = BN055sensor.calibration_status
    return IMUdata, IMUdataUnits

def writeIMUData_BN055(IMUdata, LOGFILE_PATH, IMUdataUnits={}):
    FILE_JUST_CREATED=False
    # Check if file exists
    if not(os.path.exists(LOGFILE_PATH)):
        # Open/Create csv file
        outputFile = open(LOGFILE_PATH, "w")
        FILE_JUST_CREATED=True
    else: 
        # File exists --> Append
        outputFile = open(LOGFILE_PATH, "a")

    # For csv file
    csvFileWriter = csv.writer(outputFile)

    if FILE_JUST_CREATED:
        # Write headers
        headers = IMUdata.keys()
        csvFileWriter.writerow(headers) # If empty write headers
        if len(IMUdataUnits.keys()) == len(headers):
            csvFileWriter.writerow(IMUdataUnits.values()) # Write units

    values = IMUdata.values() # Convert dictionary to lists
    csvFileWriter.writerow(values) # Write data to file

    # Close csv file
    outputFile.close()

    return 0

def main():   
    IMUdata = {} # Data dictionary
    IMUdataUnits = {} # Data units dictionary
    elapsed_time = 0.0 # [s]
    SleepTime = 1.0 / BNO_UPDATE_FREQUENCY_HZ

    startTime = time.time() # Time since January 1, 1970
    print_counter = 0
    PRINT_DELTA_TIME = BNO_UPDATE_FREQUENCY_HZ/10

    # Create output file path if not existing
    # outputFilePath = os.makedirs()
    print('DATA LOGGING STARTED')
    print('LOG_TIME: ', LOG_TIME, 'seconds')

    while elapsed_time <= LOG_TIME:
        IMUdata['Timetag'] = startTime + elapsed_time
        # Read and Write data to dictionary
        (IMUdata, IMUdataUnits) = readIMUData_BN055(BN055sensor, IMUdata, IMUdataUnits)

       # Time writing to file routine and subtract to SleepTime (rough method)
        timeInit = time.perf_counter()
        writeIMUData_BN055(IMUdata, LOGFILE_PATH, IMUdataUnits)
        writingTime = time.perf_counter() - timeInit

        # Wait time to have (roughly) the desired reading frequency
        elapsed_time += (SleepTime-writingTime)
        time.sleep(SleepTime-writingTime)
        print_counter += SleepTime

        if print_counter >= PRINT_DELTA_TIME:
            print('OK after', floor(elapsed_time), '[s]')
            print_counter = 0

    return 0

if __name__ == '__main__':
    # Run script as main
    main()