#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import ICM20948 #Gyroscope/Acceleration/Magnetometer
import MPU925x #Gyroscope/Acceleration/Magnetometer
import BME280   #Atmospheric Pressure/Temperature and humidity
import LTR390   #UV
import TSL2591  #LIGHT
import SGP40
import VOC_Algorithm
import math
import machine
from machine import Pin, I2C

MPU_VAL_WIA = 0x71
MPU_ADD_WIA = 0x75
ICM_VAL_WIA = 0xEA
ICM_ADD_WIA = 0x00
ICM_SLAVE_ADDRESS = 0x68
bus = I2C(0,scl=Pin(21),sda=Pin(20),freq=400_000)

bme280 = BME280.BME280()
bme280.get_calib_param()
light = TSL2591.TSL2591()
sgp = SGP40.SGP40()
voc_sgp = VOC_Algorithm.VOC_Algorithm()
uv = LTR390.LTR390()

device_id1 = int.from_bytes(bus.readfrom_mem(int(ICM_SLAVE_ADDRESS), int(ICM_ADD_WIA), 1), 'big')
device_id2 = int.from_bytes(bus.readfrom_mem(int(ICM_SLAVE_ADDRESS), int(MPU_ADD_WIA), 1), 'big')
if device_id1 == ICM_VAL_WIA:
    mpu = ICM20948.ICM20948()
    print("ICM20948 9-DOF I2C address:0X68")
elif device_id2 == MPU_VAL_WIA:
    mpu = MPU925x.MPU925x()
    print("MPU925x 9-DOF I2C address:0X68")
    
print("TSL2591 Light I2C address:0X29")
print("LTR390 UV I2C address:0X53")
print("SGP40 VOC I2C address:0X59")
print("bme280 T&H I2C address:0X76")

last_accel = 0
current_accel = 0
still_time = 0
movement_strikes = 0
recent_movement = []
try:
 while True:
        time.sleep(1)
        bme = []
        bme = bme280.readData()
        pressure = round(bme[0], 2) 
        temp = round(bme[1], 2) 
        hum = round(bme[2], 2)
        
        lux = round(light.Lux(), 2)
        
        uvs = uv.UVS()
        
        gas = round(sgp.raw(), 2)
        voc = voc_sgp.VocAlgorithm_process(gas)
        icm = []
        icm = mpu.ReadAll()

        # NAP PROCESSING
        last_accel = current_accel
        current_accel = math.sqrt(icm[3]**2 + icm[4]**2 + icm[5]**2)
        accel_delta = abs(current_accel - last_accel)

        # Check if change in acceleration was substantial
        if accel_delta <= 1000:
            print('current acceleration %d and last acceleration %d within 1000'%(current_accel, last_accel))
            print("position change = %d" %accel_delta)
            # No substantial movement = 0
            recent_movement.append(0)
            # Keep recent history to last 10 movements
            if len(recent_movement) > 10:
                recent_movement.pop(0)
            # Count how long the host has been still
            still_time+=1
            # If the host has been still for a minute or more they are napping
            if still_time >= 60:
                print("ACTIVE NAP: %d seconds" %still_time)
        else:
            print('movement detected: last position = %d | current position = %d'%(last_accel, current_accel))
            print("position change = %d" %accel_delta)
            # Substantial movement = 1
            recent_movement.append(1)
            # Keep recent history to last 10 movements
            if len(recent_movement) > 10:
                recent_movement.pop(0)
            # Check if there has been frequent movement during the last 10 seconds of the nap
            if still_time >= 60 and sum(recent_movement) >= 5:
                print("NAP END: %d second nap" %still_time)
                still_time = 0
        print("==================================================")
        #print("pressure : %7.2f hPa" %pressure)
        #print("temp : %-6.2f ℃" %temp)
        #print("hum : %6.2f ％" %hum)
        #print("lux : %d " %lux)
        #print("uv : %d " %uvs)
        #print("gas : %6.2f " %gas)
        #print("VOC : %d " %voc)
        #print('Roll = %.2f , Pitch = %.2f , Yaw = %.2f'%(icm[0],icm[1],icm[2]))
        #print('Acceleration:  X = %d , Y = %d , Z = %d'%(icm[3],icm[4],icm[5]))  
        #print('Gyroscope:     X = %d , Y = %d , Z = %d'%(icm[6],icm[7],icm[8]))
        #print('Magnetic:      X = %d , Y = %d , Z = %d'%((icm[9]),icm[10],icm[11]))
        #time.sleep(0.1)
except KeyboardInterrupt:
    exit()


