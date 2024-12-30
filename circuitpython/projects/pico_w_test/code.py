# SPDX-FileCopyrightText: 2022 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os
import ipaddress
import wifi
import socketpool
import board
import digitalio
import time
from analogio import AnalogIn



print()
print("Connecting to WiFi")

#  connect to your SSID
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

print("Connected to WiFi")

pool = socketpool.SocketPool(wifi.radio)

#  prints MAC address to REPL
print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

#  prints IP address to REPL
print("My IP address is", wifi.radio.ipv4_address)

#  pings Google
ipv4 = ipaddress.ip_address("8.8.4.4")
print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))


led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

usb_controller = digitalio.DigitalInOut(board.A2)
usb_controller.direction = digitalio.Direction.OUTPUT


def get_voltage(pin):
    return (pin.value * 3.3) / 65536


while True:
    led.value = False
    usb_controller.value = False
    time.sleep(3)