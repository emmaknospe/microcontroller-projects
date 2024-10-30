/*
  Web client

 This sketch connects to a website (http://www.google.com)
 using a WiFi shield.

 This example is written for a network using WPA encryption. For
 WEP or WPA, change the WiFi.begin() call accordingly.

 This example is written for a network using WPA encryption. For
 WEP or WPA, change the WiFi.begin() call accordingly.

 Circuit:
 * WiFi shield attached

 created 13 July 2010
 by dlf (Metodo2 srl)
 modified 31 May 2012
 by Tom Igoe
 */

/*
 * Adafruit MCP2515 FeatherWing CAN Receiver Example
 */

#include <Adafruit_MCP2515.h>
#include <SPI.h>
#include <WiFi101.h>
#include "arduino_secrets.h"


#ifdef ESP8266
   #define CS_PIN    2
   #define INT_PIN   16
#elif defined(ESP32) && !defined(ARDUINO_ADAFRUIT_FEATHER_ESP32S2) && !defined(ARDUINO_ADAFRUIT_FEATHER_ESP32S3)
   #define CS_PIN    14
   #define INT_PIN   32
#elif defined(TEENSYDUINO)
   #define CS_PIN    8
   #define INT_PIN   3
#elif defined(ARDUINO_STM32_FEATHER)
   #define CS_PIN    PC5
   #define INT_PIN   PC7
#elif defined(ARDUINO_NRF52832_FEATHER)  /* BSP 0.6.5 and higher! */
   #define CS_PIN    27
   #define INT_PIN   30
#elif defined(ARDUINO_MAX32620FTHR) || defined(ARDUINO_MAX32630FTHR)
   #define CS_PIN    P3_2
   #define INT_PIN   P3_3
#elif defined(ARDUINO_ADAFRUIT_FEATHER_RP2040)
   #define CS_PIN    7
   #define INT_PIN   8
#elif defined(ARDUINO_ADAFRUIT_FEATHER_RP2040_CAN)
   #define CS_PIN    PIN_CAN_CS
   #define INT_PIN   PIN_CAN_INTERRUPT
#elif defined(ARDUINO_RASPBERRY_PI_PICO) || defined(ARDUINO_RASPBERRY_PI_PICO_W) // PiCowbell CAN Bus
   #define CS_PIN    20
   #define INT_PIN   21
#else
    // Anything else, defaults!
   #define CS_PIN    5
   #define INT_PIN   6
#endif

// Set CAN bus baud rate
#define CAN_BAUDRATE (500000)

Adafruit_MCP2515 mcp(CS_PIN);

///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;            // your network key Index number (needed only for WEP)

int status = WL_IDLE_STATUS;
// if you don't want to use DNS (and reduce your sketch size)
// use the numeric IP instead of the name for the server:
IPAddress server(10,0,0,128);  // numeric IP for Google (no DNS)
// char server[] = "10.0.0.128";    // name address for Google (using DNS)

// Initialize the Ethernet client library
// with the IP address and port of the server
// that you want to connect to (port 80 is default for HTTP):
WiFiClient client;

char lastPacketData[8];
bool packetReceived = false;

void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(9600);
//  while (!Serial) {
//    ; // wait for serial port to connect. Needed for native USB port only
//  }

  Serial.println("MCP2515 Receiver test!");

  if (!mcp.begin(CAN_BAUDRATE)) {
    Serial.println("Error initializing MCP2515.");
    while(1) delay(10);
  }
  Serial.println("MCP2515 chip found");

  // Configure pins for Adafruit ATWINC1500 Feather
   WiFi.setPins(8,7,4,2);

  //check for the presence of the shield:
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue:
    while (true);
  }

  // attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }
  Serial.println("Connected to wifi");
  printWiFiStatus();
  mcp.onReceive(INT_PIN, onReceive);
}

void onReceive(int packetSize) {
  // received a packet
  Serial.print("Received ");

  if (mcp.packetExtended()) {
    Serial.print("extended ");
  }

  if (mcp.packetRtr()) {
    // Remote transmission request, packet contains no data
    Serial.print("RTR ");
  }

  Serial.print("packet with id 0x");
  Serial.print(mcp.packetId(), HEX);

  if (mcp.packetRtr()) {
    Serial.print(" and requested length ");
    Serial.println(mcp.packetDlc());
  } else {
    Serial.print(" and length ");
    Serial.println(packetSize);

    // only print packet data for non-RTR packets
    int i = 0;
    while (mcp.available()) {
      char c = ((char) mcp.read());
      Serial.print(c);
      lastPacketData[i] = c;
      i++;
    }
    lastPacketData[i] = '\0';
    packetReceived = true;
    Serial.println();
  }
  // copy the packet data to the lastPacketData array
}

void loop() {
  if (packetReceived) {
    Serial.print("Sending packet to server: ");
    Serial.println(lastPacketData);
    sendPacketToServer();
    packetReceived = false;
  }
}

void sendPacketToServer() {
  Serial.println("Sending packet to server");
  if (client.connect(server, 80)) {
    client.print("GET /log/");
    client.print(lastPacketData);
    client.println(" HTTP/1.1");
    client.println("Host: 10.0.0.128");
    client.println("Connection: close");
    client.println();
    Serial.println("Packet forwarded to server");
  } else {
    Serial.println("Connection failed");
  }
}


void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}





