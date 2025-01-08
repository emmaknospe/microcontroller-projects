import board
import neopixel
import time
import busio
import digitalio
import adafruit_tlv493d
import microcontroller
import pwmio


pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

i2c = board.STEMMA_I2C()
sensor = adafruit_tlv493d.TLV493D(i2c)

output_led = board.D6
led = pwmio.PWMOut(board.D7, frequency=5000, duty_cycle=0)


def on():
    brightness = 65535
    led.duty_cycle = brightness


def on_cycle():
    # pulse LED brightness based on the current time, fading in and out slowly
    current_time = time.monotonic()
    current_time_in_cycle = current_time % 8
    if current_time_in_cycle < 4:
        brightness = int((current_time_in_cycle / 4) * 65535)
    else:
        brightness = int(((8 - current_time_in_cycle) / 4) * 65535)
    brightness = max(0, min(65535, brightness))
    led.duty_cycle = brightness


def change_cycle():
    # flash three times
    for _ in range(3):
        on()
        time.sleep(0.15)
        off()
        time.sleep(0.15)


def off():
    led.duty_cycle = 0


try:
    last_was_on = False
    while True:
        mag_vector = sensor.magnetic
        # calculate magnitude of magnetic vector
        mag_magnitude = (mag_vector[0]**2 + mag_vector[1]**2 + mag_vector[2]**2)**0.5
        if mag_magnitude > 2000:
            if not last_was_on:
                last_was_on = True
                change_cycle()
                print(f"Magnetic field detected at {mag_magnitude:.1f} intensity!")
            on_cycle()
        else:
            if last_was_on:
                last_was_on = False
                change_cycle()
                print(f"No magnetic field detected (intensity: {mag_magnitude:.1f})")
            off()
        time.sleep(0.05)
except Exception as e:
    print(f"Error: {e}")
    # reset the board
    microcontroller.reset()