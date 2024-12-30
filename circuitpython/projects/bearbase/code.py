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
import busio
import digitalio
import adafruit_tlv493d

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

i2c = board.STEMMA_I2C()
sensor = adafruit_tlv493d.TLV493D(i2c)

output_led = board.D6
led = digitalio.DigitalInOut(board.D7)
led.direction = digitalio.Direction.OUTPUT

led.value = False

while True:
    mag_vector = sensor.magnetic
    # calculate magnitude of magnetic vector
    mag_magnitude = (mag_vector[0]**2 + mag_vector[1]**2 + mag_vector[2]**2)**0.5
    if mag_magnitude > 2000:
        led.value = True
        print("Magnetic field detected!")
    else:
        led.value = False
    time.sleep(0.1)
    # rainbow cycle
    # for i in range(255):
    #     pixels.fill((i, 0, 255 - i))
    #     time.sleep(0.01)
    # for i in range(255):
    #     pixels.fill((255 - i, i, 0))
    #     time.sleep(0.01)
    # for i in range(255):
    #     pixels.fill((0, 255 - i, i))
    #     time.sleep(0.01)
    # for i in range(255):
    #     pixels.fill((i, 0, 255 - i))
    #     time.sleep(0.01)
    # for i in range(255):
    #     pixels.fill((255 - i, i, 0))
    #     time.sleep(0.01)
    # for i in range(255):
    #     pixels.fill((0, 255 - i, i))
    #     time.sleep(0.01)
