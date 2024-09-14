# SPDX-FileCopyrightText: Copyright (c) 2024 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time
import board
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
RCVRID = 0x100
MSGTIMEOUT = 5


can_bus = MCP2515(spi, cs, baudrate=500_000)
listener = can_bus.listen(timeout=MSGTIMEOUT)


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


def can_recv_msg():
    while True:
        msg = listener.receive()
        if (can_bus.transmit_error_count > 0) or (can_bus.receive_error_count > 0):
            print(f"🔴 MSG tx_err={can_bus.transmit_error_count} rx_err={can_bus.receive_error_count}")
        if msg is None:
            if DEBUG: print("🟡 MSG not received within timeout")
            continue
        if DEBUG:
            print(f"MSG {msg.data} from={hex(msg.id)}")
            blink()
        if isinstance(msg, canio.Message):
            break
        else:
            if DEBUG: print("🟡 not a canio message")
    return msg


time.sleep(3)  # wait for serial
print(f"{'='*25}")


old_bus_state = None
while True:
    bus_state = can_bus.state
    if bus_state != old_bus_state:
        print(f"🟣 BUS state changed to {bus_state}")
        old_bus_state = bus_state

    print(f"Receiving...")
    if DEBUG: print(f"MSG avail={listener.in_waiting()} unread={can_bus.unread_message_count}")
    msg = can_recv_msg()

    print(f"{'-'*25}")