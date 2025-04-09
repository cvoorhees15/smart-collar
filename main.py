import math
import time
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY
import BME280
import ICM20948
from machine import Pin, I2C

# Display setup
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, rotate=0)
display.set_backlight(0.5)
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)

# BME280 setup
bus = I2C(0, scl=Pin(21), sda=Pin(20), freq=400_000)
bme280 = BME280.BME280()
bme280.get_calib_param()

# ICM20948 setup
ICM_VAL_WIA = 0xEA
ICM_ADD_WIA = 0x00
ICM_SLAVE_ADDRESS = 0x68
device_id1 = int.from_bytes(bus.readfrom_mem(int(ICM_SLAVE_ADDRESS), int(ICM_ADD_WIA), 1), 'big')
if device_id1 == ICM_VAL_WIA:
    mpu = ICM20948.ICM20948()

# RGB LED setup
led = RGBLED(6, 7, 8)

# Temperature colors (simplified for LED only)
temp_min = 10
temp_max = 30
colors = [(0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 0, 0)]

# Acceleration setup
movement_buffer = []
stillness_counter = 0
current_acceleration = 0
active_nap_flag = False

def movement_monitor():
    global movement_buffer
    global stillness_counter
    global current_acceleration
    global last_acceleration
    global acceleration_delta
    global active_nap_flag

    # No substantial movement
    if acceleration_delta <= 1000:
        print('current acceleration %d and last acceleration %d within 1000'%(current_acceleration, last_acceleration))
        print("acceleration change = %d" %acceleration_delta)
        print(stillness_counter)
        print(movement_buffer)
        # No substantial movement = 0
        movement_buffer.append(0)
        # Cache the last 2 minutes of movement history
        if len(movement_buffer) > 120:
            movement_buffer.pop(0)
        # Count how long the host has been still
        stillness_counter+=1
        # If the host has been still for the last minute
        if stillness_counter == 60:
            active_nap_flag = True
            print("NAP STARTED")
            print(time.localtime())
        # If the host has been still for a minute or more they are napping
        if active_nap_flag == True:
            print("ACTIVE NAP: %d seconds" %stillness_counter)
    # Minor movement
    elif 1000 < acceleration_delta < 4000:
        print('minor movement detected: last acceleration = %d | current acceleration = %d'%(last_acceleration, current_acceleration))
        print("acceleration change = %d" %acceleration_delta)
        # Substantial movement = 1
        movement_buffer.append(1)
        # Cache the last 2 minutes of movement history
        if len(movement_buffer) > 120:
            movement_buffer.pop(0)
        # Check if there has been frequent movement during the last 10 seconds 
        if sum(movement_buffer[-10:]) >= 5:
            # End nap if one was active
            if active_nap_flag == True:
                active_nap_flag = False 
                print("NAP END: %d second nap" %stillness_counter)
                print(time.localtime())
            stillness_counter = 0
    # Major movement
    elif acceleration_delta > 4000:
        print('major movement detected: last acceleration = %d | current acceleration = %d'%(last_acceleration, current_acceleration))
        print("acceleration change = %d" %acceleration_delta)
        # Major movement = 2
        movement_buffer.append(2)
        # Cache the last 2 minutes of movement history
        if len(movement_buffer) > 120:
            movement_buffer.pop(0)
        # Check if there has been frequent movement during the last 10 seconds 
        if sum(movement_buffer[-10:]) >= 5:
            # End nap if one was active
            if active_nap_flag == True:
                active_nap_flag = False 
                print("NAP END: %d second nap" %stillness_counter)
                print(time.localtime())
            stillness_counter = 0
    print("==================================================")

def temperature_to_color(temp):
    temp = min(temp, temp_max)
    temp = max(temp, temp_min)
    f_index = float(temp - temp_min) / float(temp_max - temp_min)
    f_index *= len(colors) - 1
    index = int(f_index)
    if index == len(colors) - 1:
        return colors[index]
    blend_b = f_index - index
    blend_a = 1.0 - blend_b
    a = colors[index]
    b = colors[index + 1]
    return [int((a[i] * blend_a) + (b[i] * blend_b)) for i in range(3)]

while True:
    # Clear display
    display.set_pen(BLACK)
    display.clear()

    # Get BME280 readings
    bme = bme280.readData()
    temperature = round(bme[1], 2)
    pressure = round(bme[0], 2) 
    humidity = round(bme[2], 2)
    
    # Get acceleration reading from ICM20948
    icm = []
    icm = mpu.ReadAll()
    last_acceleration = current_acceleration
    current_acceleration = math.sqrt(icm[3]**2 + icm[4]**2 + icm[5]**2)
    acceleration_delta = abs(current_acceleration - last_acceleration)
    
    
    # Set LED color based on temperature
    led.set_rgb(*temperature_to_color(temperature))

    # Monitor movement
    movement_monitor()

    # Draw temperature text (larger, centered)
    display.set_pen(WHITE)
    
    # Display temperature
    display.text("Temperature: {:.1f}°C".format(temperature), 0, 120, 200, 2)
    
    # Additional data
    display.text("Humidity: {:.1f} RH".format(humidity), 0, 100, 200, 2)

    # Update display
    display.update()
    time.sleep(1)
