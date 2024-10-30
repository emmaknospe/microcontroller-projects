import time
import board
import pulseio
import neopixel
import adafruit_irremote
import audiocore
import audioio
import digitalio
import array
import math
from digitalio import DigitalInOut, Direction, Pull


ir_tx = pulseio.PulseOut(board.IR_TX, frequency=38000, duty_cycle=2 ** 15)
ir_rx = pulseio.PulseIn(board.IR_RX, maxlen=120, idle_state=True)
decoder = adafruit_irremote.NonblockingGenericDecode(ir_rx)
encoder = adafruit_irremote.GenericTransmit(header=[9000, 4500], one=[560, 1700], zero=[560, 560], trail=560)


pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.2)
pixels.brightness = 0.2


MAX_HEALTH = 10
ATTACK_CODE = (255, 2, 191, 64)

speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
speaker_enable.switch_to_output(value=True)

audio = audioio.AudioOut(board.SPEAKER)


button = DigitalInOut(board.BUTTON_A)
button.direction = Direction.INPUT
button.pull = Pull.DOWN


def play_tone(frequency, duration):
    length = 8000 // 440
    sine_wave = array.array("h", [0] * length)
    for i in range(length):
        sine_wave[i] = int(math.sin(math.pi * 2 * i / length) * (2 ** 15))
    audio.play(audiocore.RawSample(sine_wave))
    time.sleep(duration)


class LaserTagGame:
    def __init__(self):
        self.health = MAX_HEALTH
        self.is_alive = True
        self.last_shot_time = time.monotonic()
        self.shot_cooldown = 0.5
        self.update_health_display()
        ir_rx.resume()
        self.last_ir_check = time.monotonic()

    def update_health_display(self):
        """Update the NeoPixel ring to show current health"""
        pixels.fill((0, 0, 0))
        for i in range(self.health):
            if self.health <= 3:
                pixels[i] = (255, 0, 0)
            else:
                pixels[i] = (0, 255, 0)

    def fire_weapon(self):
        current_time = time.monotonic()
        if current_time - self.last_shot_time >= self.shot_cooldown:
            try:
                encoder.transmit(ir_tx, ATTACK_CODE)
                play_tone(880, 0.1)
                self.last_shot_time = current_time
                return True
            except Exception as e:
                print("Failed to fire:", e)
                return False
        return False

    def check_for_hits(self):
        for message in decoder.read():
            if isinstance(message, adafruit_irremote.IRMessage):
                if message.code == ATTACK_CODE:
                    print("Hit detected!")
                    if time.monotonic() - self.last_ir_check >= self.shot_cooldown:
                        self.take_damage()
                        self.last_ir_check = time.monotonic()
                else:
                    print("Unknown message:", message.code)
            else:
                print("Untranslateable message:", message)
                print("Pulses: ", message.pulses)
        ir_rx.clear()
        return False

    def take_damage(self):
        if self.is_alive:
            self.health -= 1
            play_tone(220, 0.1)

            if self.health <= 0:
                self.health = 0
                self.is_alive = False
                self.player_died()

            self.update_health_display()

    def player_died(self):
        for i in range(5):
            play_tone(440 - (i * 50), 0.15)
        for _ in range(3):
            pixels.fill((255, 0, 0))
            time.sleep(0.2)
            pixels.fill((0, 0, 0))
            time.sleep(0.2)

game = LaserTagGame()

while True:
    if game.is_alive:
        if button.value:
            game.fire_weapon()
        game.check_for_hits()
        time.sleep(0.01)
