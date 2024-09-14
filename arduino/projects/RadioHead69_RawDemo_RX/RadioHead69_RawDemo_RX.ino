// rf69 demo tx rx.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messaging client
// with the RH_RF69 class. RH_RF69 class does not provide for addressing
// or reliability, so you should only use RH_RF69 if you do not need the
// higher level messaging abilities.
// It is designed to work with the other example RadioHead69_RawDemo_TX.
// Demonstrates the use of AES encryption, setting the frequency and
// modem configuration.

#include <SPI.h>
#include <RH_RF69.h>
#include <Adafruit_NeoPixel.h>
#include "Adafruit_LiquidCrystal.h"
#include <RHReliableDatagram.h>

Adafruit_LiquidCrystal lcd(0);

#define NUMPIXELS        1

Adafruit_NeoPixel pixels(NUMPIXELS, PIN_NEOPIXEL, NEO_GRB + NEO_KHZ800);

/************ Radio Setup ***************/

// Change to 434.0 or other frequency, must match RX's freq!
#define RF69_FREQ 915.0

// Server address
#define SERVER_ADDRESS 2

// RP2040 wired
#define RFM69_CS   10
#define RFM69_INT  3
#define RFM69_RST  2

// Singleton instance of the radio driver
RH_RF69 rf69(RFM69_CS, RFM69_INT);

// Class to manage message delivery and receipt, using the driver declared above
RHReliableDatagram rf69_manager(rf69, SERVER_ADDRESS);

void setup() {
  pixels.begin(); // INITIALIZE NeoPixel strip object (REQUIRED)
  pixels.setBrightness(20); // not so bright
  pixels.clear(); // Set all pixel colors to 'off'
  // pixels.setPixelColor(0, pixels.Color(0, 0, 0));
  pixels.show(); // Initialize all pixels to 'off'

  Serial.begin(9600);
  //while (!Serial) delay(1); // Wait for Serial Console (comment out line if no computer)

  pixels.setPixelColor(0, pixels.Color(0, 0, 100));
  pixels.show();

  // set up the LCD's number of rows and columns:
  if (!lcd.begin(16, 2)) {
    Serial.println("Could not init backpack. Check wiring.");
    while(1);
  }
  Serial.println("Backpack init'd.");

  // Print a message to the LCD.
  lcd.print("init'd");


  pinMode(RFM69_RST, OUTPUT);
  digitalWrite(RFM69_RST, LOW);

  Serial.println("Feather RFM69 RX Test!");
  Serial.println();

  // manual reset
  digitalWrite(RFM69_RST, HIGH);
  delay(10);
  digitalWrite(RFM69_RST, LOW);
  delay(10);

  if (!rf69.init()) {
    Serial.println("RFM69 radio init failed");
    while (1);
  }
  Serial.println("RFM69 radio init OK!");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM (for low power module)
  // No encryption
  if (!rf69.setFrequency(RF69_FREQ)) {
    Serial.println("setFrequency failed");
  }

  // If you are using a high power RF69 eg RFM69HW, you *must* set a Tx power with the
  // ishighpowermodule flag set like this:
  rf69.setTxPower(20, true);  // range from 14-20 for power, 2nd arg must be true for 69HCW

  // The encryption key has to be the same as the one in the server
  uint8_t key[] = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
  rf69.setEncryptionKey(key);

  Serial.print("RFM69 radio @");  Serial.print((int)RF69_FREQ);  Serial.println(" MHz");
  lcd.clear();
  lcd.print("await @"); lcd.print((int)RF69_FREQ); lcd.print(" MHz");
  rf69_manager.setThisAddress(SERVER_ADDRESS);
  Serial.print("Address: "); Serial.println(rf69_manager.thisAddress(), HEX);

#if defined(NEOPIXEL_POWER)
  // If this board has a power control pin, we must set it to output and high
  // in order to enable the NeoPixels. We put this in an #if defined so it can
  // be reused for other boards without compilation errors
  pinMode(NEOPIXEL_POWER, OUTPUT);
  digitalWrite(NEOPIXEL_POWER, HIGH);
#endif
}

// Dont put this on the stack:
uint8_t data[] = "packrcvd";
// Dont put this on the stack:
uint8_t buf[RH_RF69_MAX_MESSAGE_LEN];

void loop() {
 if (rf69_manager.available()) {
    // Wait for a message addressed to us from the client
    uint8_t len = sizeof(buf);
    uint8_t from;
    uint8_t to;
    // alternate: recvfromAck
    if (rf69_manager.recvfromAck(buf, &len, &from, &to)) {

      buf[len] = 0; // zero out remaining string

      Serial.print("frm #"); Serial.print(from, HEX); Serial.print("to: #"); Serial.print(to, HEX);
      Serial.print(" RI:");
      Serial.print(rf69.lastRssi(), DEC);
      Serial.print(":");
      Serial.println((char*)buf);
      delay(200);
      // Send a reply back to the originator client
      // alternate: sendtoWait
      if (!rf69_manager.sendtoWait(data, sizeof(data), from))
        Serial.println("Sending failed (no ack)");

      lcd.clear();
      lcd.print("frm #"); lcd.print(from, HEX);
      lcd.print(" RI:");
      lcd.print(rf69.lastRssi(), DEC);
      lcd.setCursor(0, 1);
      lcd.print((char*)buf);
      Blink(40, 3); // blink LED 3 times, 40ms between blinks


    }
  }
}

void Blink(byte delay_ms, byte loops) {
  while (loops--) {
    pixels.setPixelColor(0, pixels.Color(0, 100, 0));
    pixels.show();
    delay(delay_ms);
    pixels.setPixelColor(0, pixels.Color(0, 0, 0));
    pixels.show();
    delay(delay_ms);
  }
}
