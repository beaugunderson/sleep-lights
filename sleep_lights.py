#!/usr/bin/env python
# coding=utf8

from __future__ import division, print_function

import colour
import sys
import logging

logging.basicConfig(level=logging.INFO)

from datetime import datetime
from numpy import interp
from phue import Bridge

WAKE_MINUTE = 8 * 60 + 30  #  8:30am

START_MINUTE = 20 * 60     #  8:00pm

END_MINUTE_BRIGHTNESS = 23 * 60 + 45  # 11:30pm
END_MINUTE_COLOR = 22 * 60 + 15  # 10:15pm

START_TEMPERATURE = 5000
END_TEMPERATURE = 2000

START_BRIGHTNESS = 255
END_BRIGHTNESS = 32

def connect_bridge():
    bridge = Bridge('192.168.1.15')
    bridge.connect()

    return bridge

def day_lights(turn_on=False):
    bridge = connect_bridge()

    temperature = 6500

    for l in bridge.lights:
        l.brightness = 255

        if l.colormode == 'ct':
            l.colortemp_k = temperature
        else:
            l.xy = list(colour.CCT_to_xy_Kang2002(temperature))

        if turn_on and not l.on:
            l.on = True


# TODO: Save the colors to a theme so that turning on the lights turns them on
# to the correct brightness/color temperature
def night_lights(now):
    bridge = connect_bridge()

    temperature = int(interp(now, [START_MINUTE, END_MINUTE_COLOR],
                             [START_TEMPERATURE, END_TEMPERATURE]))

    print('Setting color temperature to {}'.format(temperature))

    temperature_xy = list(colour.CCT_to_xy_Kang2002(temperature))

    brightness = int(interp(now, [START_MINUTE, END_MINUTE_BRIGHTNESS],
                            [START_BRIGHTNESS, END_BRIGHTNESS]))

    print('Setting brightness to {}'.format(brightness))

    for l in bridge.lights:
        # Don't set anything if the lights are off
        if not l.on:
            continue

	print('brightness {} → {}'.format(l.brightness, brightness))
        l.brightness = brightness

        if l.colormode == 'ct':
            # XXX: not used anymore?
	    print('colortemp_k {:.2f} → {:.2f}'.format(float(l.colortemp_k),
                                                       temperature))

            l.colortemp_k = temperature
        else:
            xy_1 = ['{:.3f}'.format(f) for f in l.xy]
            xy_2 = ['{:.3f}'.format(f) for f in temperature_xy]

	    print('xy {} → {}'.format(xy_1, xy_2))

            l.xy = temperature_xy

if __name__ == '__main__':
    now = datetime.now()
    now_minute = now.hour * 60 + now.minute

    if now_minute <= WAKE_MINUTE:
        sys.exit()

    if now_minute <= START_MINUTE:
        day_lights(turn_on=(now_minute - WAKE_MINUTE <= 5))
    else:
        night_lights(now_minute)
