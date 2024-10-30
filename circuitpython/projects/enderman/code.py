# SPDX-FileCopyrightText: 2023 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

'''RP2040 Prop-Maker Feather Example'''

import time
import board
import audiocore
import random
import audiobusio
import audiomixer
import pwmio
from digitalio import DigitalInOut, Direction, Pull
import neopixel
import adafruit_lis3dh

# enable external power pin
# provides power to the external components
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.direction = Direction.OUTPUT
external_power.value = True

# LED is on pin D5
led = DigitalInOut(board.D5)
led.direction = Direction.OUTPUT
led.value = True

# i2s playback
STARE = audiocore.WaveFile(open("stare.wav", "rb"))
IDLE_SOUNDS = [
    audiocore.WaveFile(open("idle1.wav", "rb")),
    audiocore.WaveFile(open("idle2.wav", "rb")),
    audiocore.WaveFile(open("idle3.wav", "rb")),
    audiocore.WaveFile(open("idle4.wav", "rb")),
    audiocore.WaveFile(open("idle5.wav", "rb")),
]


audio = audiobusio.I2SOut(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA)
mixer = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=1,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer)
# mixer.voice[0].play(STARE, loop=False)
mixer.voice[0].level = 1.0

# # external button
switch = DigitalInOut(board.EXTERNAL_BUTTON)
switch.direction = Direction.INPUT
switch.pull = Pull.UP
switch_state = False

# external neopixels
num_pixels = 20
pixels = neopixel.NeoPixel(board.EXTERNAL_NEOPIXELS, num_pixels)
pixels.brightness = 0.3

# onboard LIS3DH
i2c = board.I2C()
int1 = DigitalInOut(board.ACCELEROMETER_INTERRUPT)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
lis3dh.range = adafruit_lis3dh.RANGE_2_G
lis3dh.set_tap(2, 127)

n_iters_since_idle_sound = 0
MIN_IDLE_SOUND_ITERS = 1000
IDLE_SOUND_TICK_PROB = 0.005

PURPLE_DOTS = set()

RAGE = 0

while True:
    time.sleep(0.02)
    n_iters_since_idle_sound += 1

    # randomly turn neopixels purple if rage > 0
    if RAGE > 0:
        for i in range(num_pixels):
            if random.random() < 0.5:
                pixels[i] = (RAGE, 0, RAGE)
            else:
                pixels[i] = (0, 0, 0)
        pixels.show()
        RAGE -= 1
    else:
        # if there are no purple dots, add one
        if not PURPLE_DOTS:
            PURPLE_DOTS.add((random.randint(0, num_pixels - 1), 1, "up"))
        elif len(PURPLE_DOTS) < 3 and random.random() < 0.005:
            index = random.randint(0, num_pixels - 1)
            if not any([dot[0] == index for dot in PURPLE_DOTS]):
                PURPLE_DOTS.add((index, 1, "up"))
        new_dots = set()
        for dot in PURPLE_DOTS:
            index, brightness, direction = dot
            if direction == "up":
                if brightness < 255:
                    brightness += 2
                else:
                    direction = "down"
            else:
                if brightness > 0:
                    brightness -= 2

            if brightness > 0:
                new_dots.add((index, brightness, direction))
        PURPLE_DOTS = new_dots

        for dot in PURPLE_DOTS:
            index, brightness, _ = dot
            brightness = min(brightness, 255)
            pixels[index] = (brightness, 0, brightness)
        pixels.show()

    if lis3dh.tapped and not mixer.voice[0].playing:
        print("Tapped!")
        mixer.voice[0].play(STARE, loop=False)
        RAGE = 255
        n_iters_since_idle_sound = 0

    if not switch.value and not switch_state:
        print("Button pressed, triggering idle sound!")
        to_play = random.choice(IDLE_SOUNDS)
        switch_state = True
        mixer.voice[0].play(to_play, loop=False)
        n_iters_since_idle_sound = 0
    elif switch.value:
        switch_state = False

    if n_iters_since_idle_sound > MIN_IDLE_SOUND_ITERS and random.random() < IDLE_SOUND_TICK_PROB and not mixer.voice[0].playing:
        print("Idle sound!")
        to_play = random.choice(IDLE_SOUNDS)
        mixer.voice[0].play(to_play, loop=False)
        n_iters_since_idle_sound = 0
