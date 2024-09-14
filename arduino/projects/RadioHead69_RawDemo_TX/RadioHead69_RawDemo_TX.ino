// rf69 demo tx rx.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messaging client
// with the RH_RF69 class. RH_RF69 class does not provide for addressing
// or reliability, so you should only use RH_RF69 if you do not need the
// higher level messaging abilities.
// It is designed to work with the other example RadioHead69_RawDemo_RX.
// Demonstrates the use of AES encryption, setting the frequency and
// modem configuration.

#include <SPI.h>
#include <RH_RF69.h>
#include <Adafruit_NeoPixel.h>
#include <RHReliableDatagram.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include "Adafruit_seesaw.h"

// Seesaw constants
#define SS_SWITCH_SELECT 1
#define SS_SWITCH_UP     2
#define SS_SWITCH_LEFT   3
#define SS_SWITCH_DOWN   4
#define SS_SWITCH_RIGHT  5

#define SEESAW_ADDR      0x49

Adafruit_seesaw ss;
int32_t encoder_position;

#define NUMPIXELS        1

Adafruit_NeoPixel pixels(NUMPIXELS, PIN_NEOPIXEL, NEO_GRB + NEO_KHZ800);


#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define SCREEN_ADDRESS 0x3D ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
#define WIRE Wire // Stemma QT I2C bus
#define OLED_RESET -1 // Reset pin #

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

/************ Radio Setup ***************/

#define CLIENT_ADDRESS 1
#define SERVER_ADDRESS 2


// Change to 434.0 or other frequency, must match RX's freq!
#define RF69_FREQ 915.0

// RP2040 wired
#define RFM69_CS   10
#define RFM69_INT  3
#define RFM69_RST  2

// Singleton instance of the radio driver
RH_RF69 rf69(RFM69_CS, RFM69_INT);

// Class to manage message delivery and receipt, using the driver declared above
RHReliableDatagram rf69_manager(rf69, CLIENT_ADDRESS);

int16_t packetnum = 0;  // packet counter, we increment per xmission

void setup() {
  Serial.begin(9600);
  while (!Serial) delay(1); // Wait for Serial Console (comment out line if no computer)

  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  Serial.println("Looking for seesaw!");

  if (! ss.begin(SEESAW_ADDR)) {
    Serial.println("Couldn't find seesaw on default address");
  }

  Serial.println("seesaw started");
  uint32_t version = ((ss.getVersion() >> 16) & 0xFFFF);
  if (version  != 5740){
    Serial.print("Wrong firmware loaded? ");
    Serial.println(version);
    while(1) delay(10);
  }
  Serial.println("Found Product 5740");

  ss.pinMode(SS_SWITCH_UP, INPUT_PULLUP);
  ss.pinMode(SS_SWITCH_DOWN, INPUT_PULLUP);
  ss.pinMode(SS_SWITCH_LEFT, INPUT_PULLUP);
  ss.pinMode(SS_SWITCH_RIGHT, INPUT_PULLUP);
  ss.pinMode(SS_SWITCH_SELECT, INPUT_PULLUP);

  // get starting position
  encoder_position = ss.getEncoderPosition();

  Serial.println("Turning on interrupts");
  ss.enableEncoderInterrupt();
  ss.setGPIOInterrupts((uint32_t)1 << SS_SWITCH_UP, 1);

  // Show initial display buffer contents on the screen --
  // the library initializes this with an Adafruit splash screen.
  display.display();

  pinMode(RFM69_RST, OUTPUT);
  digitalWrite(RFM69_RST, LOW);

  Serial.println("Feather RFM69 TX Test!");
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

  rf69_manager.setThisAddress(CLIENT_ADDRESS);
  Serial.print("Address: ");
  Serial.println(rf69_manager.thisAddress(), HEX);
  rf69_manager.setTimeout(500);
}

// Dont put this on the stack:
uint8_t buf[RH_RF69_MAX_MESSAGE_LEN];





//void loop() {
//  pixels.setPixelColor(0, pixels.Color(0, 0, 100));
//  pixels.show();
//  delay(1000);  // Wait 1 second between transmits, could also 'sleep' here!
//  pixels.setPixelColor(0, pixels.Color(0, 0, 0));
//  pixels.show();
//
//  itoa(packetnum++, (char*) data+5, 10);
//  Serial.print("Sending "); Serial.print((char*)data); Serial.print(" to "); Serial.println(SERVER_ADDRESS);
//
//  if (rf69_manager.sendtoWait(data, sizeof(data), SERVER_ADDRESS)) {
//    // Now wait for a reply from the server
//    uint8_t len = sizeof(buf);
//    uint8_t from;
//    if (rf69_manager.recvfromAckTimeout(buf, &len, 2000, &from)) {
//      buf[len] = 0; // zero out remaining string
//
//      Serial.print("Got reply from #"); Serial.print(from, HEX);
//      Serial.print(" [RSSI :");
//      Serial.print(rf69.lastRssi());
//      Serial.print("] : ");
//      Serial.println((char*)buf);
//      Blink(40, 3); // blink LED 3 times, 40ms between blinks
//    } else {
//      Serial.println("No reply, is anyone listening?");
//    }
//  } else {
//    Serial.println("Sending failed (no ack)");
//  }
//}

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

uint8_t data[64] = " ";
uint8_t current_char_index = 0;
uint8_t current_length = 1;

char current_char = 'A';

void text_entry_init(void) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE, SSD1306_BLACK);
    display.setCursor(0, 0);
    display.display();
    data[0] = 'A';
    data[1] = '\0';
    current_char_index = 0;
    current_length = 1;
}

void text_entry(void) {
    text_entry_init();
    // read rotary encoder input, slide through alphabet
    while (1) {
        int32_t new_position = ss.getEncoderPosition();
        // did we move around?
        if (encoder_position != new_position) {
            data[current_char_index] = (((data[current_char_index] - 'A') + (new_position - encoder_position)) % 26) + 'A';
            display.setCursor(0, 0);
            display.print((char*) data);
            display.display();
            encoder_position = new_position;      // and save for next round
        }
        // check for button press
        if (! ss.digitalRead(SS_SWITCH_SELECT)) {
            // move to the next character
            current_char_index++;
            // if current_char_index is greater than current_length, we need to increase the length
            if (current_char_index >= current_length) {
                // fill this element with the last character
                data[current_length] = data[current_length-1];
                // fill the next element with null to delimit
                data[current_length+1] = '\0';
                // increase the length
                current_length++;
            }
            display.display();
            // debounce
            while (! ss.digitalRead(SS_SWITCH_SELECT)) {
                delay(10);
            }
        }
        // exit on left press
        if (! ss.digitalRead(SS_SWITCH_LEFT)) {
            break;
        }
        delay(10);
    }
}


void loop() {
    text_entry();
    // text is now entered, transmit
    Serial.print("Sending "); Serial.print((char*)data); Serial.print(" to "); Serial.println(SERVER_ADDRESS);
    if (rf69_manager.sendtoWait(data, current_length, SERVER_ADDRESS)) {
        // Now wait for a reply from the server
        uint8_t len = sizeof(buf);
        uint8_t from;
        if (rf69_manager.recvfromAckTimeout(buf, &len, 2000, &from)) {
            buf[len] = 0; // zero out remaining string
            Serial.print("Got reply from #"); Serial.print(from, HEX);
            Serial.print(" [RSSI :");
            Serial.print(rf69.lastRssi());
            Serial.print("] : ");
            Serial.println((char*)buf);
            Blink(40, 3); // blink LED 3 times, 40ms between blinks
        } else {
            Serial.println("No reply, is anyone listening?");
        }
    } else {
        Serial.println("Sending failed (no ack)");
    }
}