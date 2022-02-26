#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Boot script

Do initial stuff here, similar to the setup() function on Arduino

Connect to network, create an AccessPoint if connection failed otherwise
"""

# system packages
import esp
import gc
import machine
import network
import time

# custom modules
from be_helpers.generic_helper import GenericHelper
from be_helpers.led_helper import Led, Neopixel


# set clock speed to 240MHz instead of default 160MHz
# import machine
# machine.freq(240000000)

# disable ESP os debug output
esp.osdebug(None)

led = Led()
pixel = Neopixel()
# turn Neopixel and onboard LED off
led.turn_off()
pixel.clear()

# flash onboard LED 3 times
led.flash(amount=3, delay_ms=50)

# turn onboard LED on
led.turn_on()

station = network.WLAN(network.STA_IF)
if station.active() and station.isconnected():
    station.disconnect()
    time.sleep(1)
station.active(False)
time.sleep(1)
station.active(True)

station.connect('SSID', 'PASSWORD')
time.sleep(1)

result = station.isconnected()
# force an accesspoint creation
# result = False

if result is False:
    # disconnect as/from station and disable WiFi for it
    station.disconnect()
    station.active(False)
    time.sleep(1)

    # create a true AccessPoint without any active Station mode
    accesspoint = network.WLAN(network.AP_IF)

    # activate accesspoint if not yet enabled
    if not accesspoint.active():
        accesspoint.active(True)

    accesspoint.config(essid="MicroPython AP",
                       authmode=network.AUTH_OPEN,
                       password='',
                       channel=11)

    print('Created Accesspoint')
else:
    print('Successfully connected to a network :)')

# turn Neopixel and onboard LED off
led.turn_off()
pixel.clear()

print('Restart cause: {}'.format(machine.reset_cause()))
print('RAM info: {}'.format(GenericHelper.free(full=True)))

# run garbage collector at the end to clean up
gc.collect()
