#include <Adafruit_NeoPixel.h>

// How many internal neopixels do we have? some boards have more than one!
#define NUMPIXELS        1

Adafruit_NeoPixel pixels(NUMPIXELS, PIN_NEOPIXEL, NEO_GRB + NEO_KHZ800);

// the setup routine runs once when you press reset:
void setup() {
  Serial.begin(115200);

#if defined(NEOPIXEL_POWER)
  // If this board has a power control pin, we must set it to output and high
  // in order to enable the NeoPixels. We put this in an #if defined so it can
  // be reused for other boards without compilation errors
  pinMode(NEOPIXEL_POWER, OUTPUT);
  digitalWrite(NEOPIXEL_POWER, HIGH);
#endif

  pixels.begin(); // INITIALIZE NeoPixel strip object (REQUIRED)
  pixels.setBrightness(20); // not so bright
  pixels.clear(); // Set all pixel colors to 'off'
}

// the loop routine runs over and over again forever:
void loop() {
  // pixels.setPixelColor(0, pixels.Color(150, 0, 0));
  // pixels.show();
  // delay(50);
  // Do rainbow
  for (int i=0; i<256; i++) {
    pixels.setPixelColor(0, pixels.Color(255-i, i, 0));
    pixels.show();
    delay(10);
  }
    for (int i=0; i<256; i++) {
        pixels.setPixelColor(0, pixels.Color(0, 255-i, i));
        pixels.show();
        delay(10);
    }
    for (int i=0; i<256; i++) {
        pixels.setPixelColor(0, pixels.Color(i, 0, 255-i));
        pixels.show();
        delay(10);
    }
}