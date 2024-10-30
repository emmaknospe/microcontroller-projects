from adafruit_circuitplayground import cp
import time
import math

def rainbow_cycle():
    """
    Creates a smooth rainbow animation using the NeoPixels
    """
    while True:
        for i in range(10):
            cp.pixels[i] = ((i * 255 // 10), 255 - (i * 255 // 10), 50)
        cp.pixels.brightness = 0.3
        time.sleep(0.05)


def sound_meter():
    """
    Uses the microphone to create a sound-reactive LED display
    """
    while True:
        # Get sound level and map it to number of pixels
        sound = cp.sound_level
        num_pixels = int(sound / 512 * 10)

        # Light up pixels based on sound level
        for i in range(10):
            if i < num_pixels:
                cp.pixels[i] = (0, 255, 0)
            else:
                cp.pixels[i] = (0, 0, 0)
        time.sleep(0.05)


def tilt_game():
    """
    Precise tilt indicator using a single LED
    LED positions:
    7  6  5
    8     4
    9  0  3
    1     2
    """
    while True:
        x, y, z = cp.acceleration

        # Clear all pixels
        cp.pixels.fill((0, 0, 0))

        # Calculate angle of tilt
        angle = math.atan2(y, x)
        # Convert to degrees and adjust so 0 is at the top
        angle_deg = (math.degrees(angle) + 90) % 360

        # Calculate which LED to light based on angle
        # The LEDs are positioned in a circle, each covering 36 degrees
        led_position = int((angle_deg + 18) / 36) % 10

        # Calculate tilt magnitude
        magnitude = math.sqrt(x * x + y * y)

        # Only light up LED if tilt is significant enough
        if magnitude > 0.5:
            # Use magnitude to determine brightness (up to 1.0)
            brightness = min(magnitude / 9.8, 1.0)  # 9.8 is roughly 1G
            cp.pixels[led_position] = (int(255 * brightness), 0, int(255 * brightness))

        time.sleep(0.05)


tilt_game()