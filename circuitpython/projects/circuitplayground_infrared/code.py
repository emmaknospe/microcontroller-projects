# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import pulseio
import board
from adafruit_circuitplayground.express import cpx
import adafruit_irremote
import time

# Create a 'pulseio' input, to listen to infrared signals on the IR receiver
pulsein = pulseio.PulseIn(board.IR_RX, maxlen=120, idle_state=True)
# Create a decoder that will take pulses and turn them into numbers
decoder = adafruit_irremote.GenericDecode()

# Create a 'pulseio' output, to send infrared signals on the IR transmitter @ 38KHz
pulseout = pulseio.PulseOut(board.IR_TX, frequency=38000, duty_cycle=2 ** 15)
# Create an encoder that will take numbers and turn them into NEC IR pulses
encoder = adafruit_irremote.GenericTransmit(header=[9000, 4500],
                                            one=[560, 1700],
                                            zero=[560, 560],
                                            trail=0)

GE_TEMP_UP = (129, 102, 161, 94)
GE_TEMP_DOWN = (129, 102, 81, 174)
GE_POWER = (129, 102, 129, 126)
GE_FAN = (129, 102, 153, 102)
GE_MODE = (129, 102, 217, 38)

KNOWN_CODES = {
    GE_TEMP_UP: "GE Temp Up",
    GE_TEMP_DOWN: "GE Temp Down",
    GE_POWER: "GE Power",
    GE_FAN: "GE Fan",
    GE_MODE: "GE Mode",
}


def read():
    while True:
        pulses = decoder.read_pulses(pulsein)
        try:
            # Attempt to convert received pulses into numbers
            received_code = decoder.decode_bits(pulses)
        except adafruit_irremote.IRNECRepeatException:
            # We got an unusual short code, probably a 'repeat' signal
            # print("NEC repeat!")
            continue
        except adafruit_irremote.IRDecodeException as e:
            # Something got distorted or maybe its not an NEC-type remote?
            # print("Failed to decode: ", e.args)
            continue

        print("NEC Infrared code received: ", received_code)
        if tuple(received_code) in KNOWN_CODES:
            print("Known code: ", KNOWN_CODES[tuple(received_code)])

def write():
    while True:
        if cpx.button_a:
            print("Button A pressed! \n")
            cpx.red_led = True
            encoder.transmit(pulseout, GE_TEMP_UP)
            cpx.red_led = False
            # wait so the receiver can get the full message
            time.sleep(0.2)
        if cpx.button_b:
            print("Button B pressed! \n")
            cpx.red_led = True
            encoder.transmit(pulseout, GE_TEMP_DOWN)
            cpx.red_led = False
            time.sleep(0.2)

write()