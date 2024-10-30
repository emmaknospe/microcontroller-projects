# SPDX-FileCopyrightText: 2022 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os
import ipaddress
import wifi
import socketpool
import board
import digitalio
import time
import adafruit_requests
import adafruit_connection_manager
import json
import gc
import microcontroller


def wifi_connect():
    print("Connecting to WiFi")

    #  connect to your SSID
    ssid = os.getenv('CIRCUITPY_WIFI_SSID')
    wifi.radio.connect(ssid, os.getenv('CIRCUITPY_WIFI_PASSWORD'))

    print("Connected to WiFi")

    pool = socketpool.SocketPool(wifi.radio)
    ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl_context)

    #
    # #  prints IP address to REPL
    print("My IP address is", wifi.radio.ipv4_address)
    #
    # #  pings Google
    ipv4 = ipaddress.ip_address("8.8.4.4")
    print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))
    return requests


class ResetError(Exception):
    pass


def get_settings(requests):
    bucket_name = 'homelab306'
    object_key = 'plantlamp/settings.json'

    url = f'https://{bucket_name}.s3.amazonaws.com/{object_key}'
    response = None
    try:
        failure_count = 0
        while True:
            try:
                # Send a GET request to retrieve the settings JSON
                with requests.get(url) as response:
                    # Check if the request was successful
                    if response.status_code == 200:
                        # Parse the JSON response
                        settings = json.loads(response.text)
                        return settings
                    else:
                        raise Exception(f'Error retrieving settings: {response.status_code}')

            except Exception as e:
                print(f'Error retrieving settings: {e}')
                failure_count += 1
                time.sleep(5)
                if failure_count > 3:
                    raise ResetError()
    finally:
        if response:
            response.close()


led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


def main():
    # set relay on pin 1
    relay = digitalio.DigitalInOut(board.GP1)
    relay.direction = digitalio.Direction.OUTPUT
    # relay.value = 1

    requests = wifi_connect()
    settings = get_settings(requests)

    count = 0

    while True:
        time.sleep(2)
        if count % 2 == 0:
            print('Checking settings...')
            new_settings = get_settings(requests)
            if new_settings:
                settings["on"] = new_settings["on"]
            if settings["on"]:
                relay.value = 1
            else:
                relay.value = 0
        count += 1
        if (count % 60) == 0:
            gc.collect()
            count = 0

try:
    main()
except Exception as e:
    print('Resetting: ', e)
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()




