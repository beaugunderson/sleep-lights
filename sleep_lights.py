#!/usr/bin/env python

from __future__ import division, print_function

import colour
import sys
import logging

logging.basicConfig(level=logging.INFO)

from datetime import datetime
from numpy import interp
from phue import Bridge

WAKE_MINUTE = 8 * 60 + 30  #  8:30am

START_MINUTE = 19 * 60     #  7:00pm
END_MINUTE = 23 * 60 + 59  # 11:59pm

START_TEMPERATURE = 6500
END_TEMPERATURE = 2500

START_BRIGHTNESS = 255
END_BRIGHTNESS = 127

def connect_bridge():
    bridge = Bridge('192.168.1.15')
    bridge.connect()

    return bridge

def day_lights():
    bridge = connect_bridge()

    temperature = 6500

    for l in bridge.lights:
        l.brightness = 255

        if l.colormode == 'ct':
            l.colortemp_k = temperature
        else:
            l.xy = list(colour.CCT_to_xy_Kang2002(temperature))

def night_lights(now):
    bridge = connect_bridge()

    temperature = int(interp(now, [START_MINUTE, END_MINUTE],
                             [START_TEMPERATURE, END_TEMPERATURE]))

    brightness = int(interp(now, [START_MINUTE, END_MINUTE],
                            [START_BRIGHTNESS, END_BRIGHTNESS]))

    for l in bridge.lights:
        # Don't set anything if the lights are off
        if not l.on:
            continue

        l.brightness = brightness

        if l.colormode == 'ct':
            l.colortemp_k = temperature
        else:
            l.xy = list(colour.CCT_to_xy_Kang2002(temperature))

if __name__ == '__main__':
    now = datetime.now()
    now_minute = now.hour * 60 + now.minute

    if now_minute <= WAKE_MINUTE:
        sys.exit()

    if now_minute <= START_MINUTE:
        day_lights()
    else:
        night_lights(now_minute)
