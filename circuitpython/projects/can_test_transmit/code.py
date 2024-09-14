# SPDX-FileCopyrightText: Copyright (c) 2024 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time
import board
import random
from digitalio import DigitalInOut
from adafruit_mcp2515 import MCP2515
import adafruit_mcp2515.canio as canio


import neopixel

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)


cs = DigitalInOut(board.D10)
cs.switch_to_output()
spi = board.SPI()



#
# CAN LISTENER
#
DEBUG = True
SENDERID = 0x400


def blink():
    pixels.fill((255, 0, 255))
    time.sleep(0.1)
    pixels.fill((0, 0, 0))
    pixels.fill((255, 0, 255))
    time.sleep(0.1)
    pixels.fill((0, 0, 0))
    pixels.fill((255, 0, 255))
    time.sleep(0.1)
    pixels.fill((0, 0, 0))


def can_send_msg(data):
    message = canio.Message(id=SENDERID, data=data)
    can_bus.send(message)
    if (can_bus.transmit_error_count > 0) or (can_bus.receive_error_count > 0):
        print(f"🔴 MSG tx_err={can_bus.transmit_error_count} rx_err={can_bus.receive_error_count}")
    else:
        blink()
    print(f"MSG {data} len={len(data)}")
    return


time.sleep(3)  # wait for serial
print(f"{'='*25}")

can_bus = MCP2515(spi, cs, baudrate=500_000)


old_bus_state = None
while True:
    bus_state = can_bus.state
    if bus_state != old_bus_state:
        print(f"🟣 BUS state changed to {bus_state}")
        old_bus_state = bus_state

    print(f"Sending...")
    data = "".join(random.choice("0123456789ABCDEF") for i in range(random.randint(1, 6))).encode()
    can_send_msg(data)

    print(f"{'-'*25}")
    time.sleep(1)