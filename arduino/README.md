Compile command example:
```bash
arduino-cli compile -b rp2040:rp2040:adafruit_kb2040 --libraries ./libraries
```

Upload command example:
```bash
arduino-cli upload -b rp2040:rp2040:adafruit_kb2040 -p /dev/cu.usbmodem14101
```

Serial monitor command example:
```bash
arduino-cli monitor  -p /dev/cu.usbmodem14101
```