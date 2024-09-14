# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Blink example for boards with ONLY a NeoPixel LED (e.g. without a built-in red LED).
Includes QT Py and various Trinkeys.

Requires two libraries from the Adafruit CircuitPython Library Bundle.
Download the bundle from circuitpython.org/libraries and copy the
following files to your CIRCUITPY/lib folder:
* neopixel.mpy
* adafruit_pixelbuf.mpy

Once the libraries are copied, save this file as code.py to your CIRCUITPY
drive to run it.
"""
import time
import board
import neopixel

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

while True:
    # rainbow cycle
    for i in range(255):
        pixels.fill((i, 0, 255 - i))
        time.sleep(0.01)
    for i in range(255):
        pixels.fill((255 - i, i, 0))
        time.sleep(0.01)
    for i in range(255):
        pixels.fill((0, 255 - i, i))
        time.sleep(0.01)
    for i in range(255):
        pixels.fill((i, 0, 255 - i))
        time.sleep(0.01)
    for i in range(255):
        pixels.fill((255 - i, i, 0))
        time.sleep(0.01)
    for i in range(255):
        pixels.fill((0, 255 - i, i))
        time.sleep(0.01)
