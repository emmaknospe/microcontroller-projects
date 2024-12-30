# SPDX-FileCopyrightText: 2022 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os
import ipaddress
import wifi
import socketpool
import board
import digitalio
import neopixel
import time
from analogio import AnalogIn
from adafruit_neokey.neokey1x4 import NeoKey1x4
import array
import pulseio
import adafruit_irremote


# Create a 'PulseOut' to send infrared signals on the IR transmitter @ 38KHz
pulseout = pulseio.PulseOut(board.A2, frequency=38000, duty_cycle=2**15)
# Create an encoder that will take numbers and turn them into NEC IR pulses
encoder = adafruit_irremote.GenericTransmit(header=[9000, 4500],
                                            one=[560, 1700],
                                            zero=[560, 560],
                                            trail=0)

ir_receiver = pulseio.PulseIn(board.A3, maxlen=120, idle_state=True)
decoder = adafruit_irremote.GenericDecode()



neokey = NeoKey1x4(board.STEMMA_I2C(), addr=0x30)



print()
print("Connecting to WiFi")

#  connect to your SSID
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

print("Connected to WiFi")

pool = socketpool.SocketPool(wifi.radio)

# MODE = "pico_w"
MODE = "qt_py"

if MODE == "pico_w":
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT

    def set_led(value):
        led.value = value


    usb_controller = digitalio.DigitalInOut(board.GP15)
    usb_controller.direction = digitalio.Direction.OUTPUT
    analog_in = AnalogIn(board.A2)
elif MODE == "qt_py":
    board_neopixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

    def set_led(value):
        if value:
            board_neopixel[0] = (100, 0, 0)
        else:
            board_neopixel[0] = (0, 0, 0)


    usb_controller = digitalio.DigitalInOut(board.A1)
    usb_controller.direction = digitalio.Direction.OUTPUT
    analog_in = AnalogIn(board.A0)


def get_voltage(pin):
    return (pin.value * 3.3) / 65536


def get_usb_status():
    in_voltage = get_voltage(analog_in)
    if in_voltage > 1:
        return "left"
    else:
        return "right"


def test_usb():
    while True:
        set_led(True)
        usb_controller.value = True
        print("Toggle")
        time.sleep(0.1)
        set_led(False)
        usb_controller.value = False
        time.sleep(3)
        print(get_usb_status())
        time.sleep(0.1)


def test_ir():
    while True:
        pulses = decoder.read_pulses(ir_receiver)
        try:
            # Attempt to decode the received pulses
            received_code = decoder.decode_bits(pulses)
            if received_code:
                hex_code = ''.join(["%02X" % x for x in received_code])
                print(f"Received: {hex_code}")
                # Convert pulses to an array of type 'H' (unsigned short)
                pulse_array = array.array('H', pulses)
                # send code back using original pulses
                pulseout.send(pulse_array)
                print(f"Sent: {pulse_array}")
        except adafruit_irremote.IRNECRepeatException:  # Signal was repeated, ignore
            pass
        except adafruit_irremote.IRDecodeException:  # Failed to decode signal
            print("Error decoding")
        ir_receiver.clear()  # Clear the receiver buffer
        time.sleep(1)  # Delay to allow the receiver to settle
        print()


def toggle_state():
    set_led(True)
    usb_controller.value = True
    print("Toggle")
    time.sleep(0.1)
    set_led(False)
    usb_controller.value = False


PURPLE = 0xA020F0
GREEN = 0x00A36C

def set_colors_all(color):
    for i in range(0, 4):
        neokey.pixels[i] = color


def set_state(desired_state, current_state):
    if current_state != desired_state:
        toggle_state()

def main():
    while True:
        state = get_usb_status()
        if state == "left":
            set_colors_all(PURPLE)
        elif state == "right":
            set_colors_all(GREEN)

        if neokey[0] and state == "right":
            print("set state left")
            set_state("left", current_state=state)
        elif neokey[0] and state == "left":
            print("set state right")
            set_state("right", current_state=state)

        time.sleep(0.07)


# main()
test_ir()