import ipaddress
import json
import os
import time
import microcontroller
import adafruit_connection_manager
import adafruit_requests
import board
import neopixel
import socketpool
import wifi
from adafruit_httpserver import (
    Server,
    REQUEST_HANDLED_RESPONSE_SENT,
    Request,
    Redirect,
    FileResponse,
    Response
)
import asyncio

from palettes import rainbow, bisexual_flag, trans_flag, lesbian_flag, gay_flag, club, seafoam, strobe, fast_club, fast_seafoam
from patterns import slide, pulse


PALETTE_FNS = {
    'club': club,
    'seafoam': seafoam,
    'strobe': strobe,
    'fast_club': fast_club,
    'fast_seafoam': fast_seafoam,
    'incandescent_soft': lambda index: (140, 110, 30, 0),
    'neon_yellow': lambda index: (255, 255, 0, 0),
    'neon_green': lambda index: (57, 255, 20, 0),
    'rainbow': rainbow,
    'bisexual_flag': bisexual_flag,
    'trans_flag': trans_flag,
    'lesbian_flag': lesbian_flag,
    'gay_flag': gay_flag
}

PATTERN_FNS = {
    'slide': slide,
    'pulse': pulse,
}

def wifi_connect(mode="server"):
    ssid = os.getenv('CIRCUITPY_WIFI_SSID')

    print(f"Connecting to WiFi at {ssid}")

    wifi.radio.connect(ssid, os.getenv('CIRCUITPY_WIFI_PASSWORD'))

    print("Connected to WiFi")

    pool = socketpool.SocketPool(wifi.radio)
    if mode == "server":
        return Server(pool, "/static", debug=True)
    else:
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



server = wifi_connect()


N_PIXELS = 37
# 0.035 seconds per loop
LOOP_TIME = 0.035
N_LOOPS_BETWEEN_CHECKS = 4 / LOOP_TIME
PIN = board.GP22
np_strip = neopixel.NeoPixel(PIN, N_PIXELS, bpp=3, auto_write=False)


SETTINGS = {"state": "on", "palette": "seafoam", "pattern": "pulse", "debounce": 5}


@server.route("/", methods=["GET"])
def base(request):
    palette_selector = "".join([
        f'<option value="{palette}" {"selected" if palette == SETTINGS.get("palette", None) else ""}>{palette}</option>'
        for palette in PALETTE_FNS.keys()
    ])
    pattern_selector = "".join([
        f'<option value="{pattern}" {"selected" if pattern == SETTINGS.get("pattern", None) else ""}>{pattern}</option>'
        for pattern in PATTERN_FNS.keys()
    ])
    current_debounce = SETTINGS.get("debounce", 5)
    return Response(request, body=f"""
    <html>
    <head>
        <title>Pride Bar</title>
        </head>
        <body>
            <h1>Pride Bar</h1>
            <p>Change the settings of the pride bar</p>
            <form action="/settings" method="post">
                <label for="palette">Palette:</label>
                <select name="palette" id="palette">
                    {palette_selector}
                </select>
                <br>
                <label for="pattern">Pattern:</label>
                <select name="pattern" id="pattern">
                    {pattern_selector}
                </select>
                <br>
                <label for="debounce">Debounce:</label>
                <input type="number" id="debounce" name="debounce" min="0" max="10" value="{current_debounce}">
                <br>
                <label for="state">State:</label>
                <select name="state" id="state">
                    <option value="on" {"selected" if SETTINGS['state'] == 'on' else ""}>On</option>
                    <option value="off" {"selected" if SETTINGS['state'] == 'off' else ""}>Off</option>
                <br>
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """, content_type="text/html")


@server.route("/settings", methods=["POST"])
def settings(request):
    SETTINGS['palette'] = request.form_data.get('palette', 'rainbow')
    SETTINGS['pattern'] = request.form_data.get('pattern', 'slide')
    SETTINGS['debounce'] = int(request.form_data.get('debounce', 5))
    SETTINGS['state'] = request.form_data.get('state', 'off')
    return Redirect(request, "/")


def get_settings(requests):
    bucket_name = 'homelab306'
    object_key = 'pride/settings.json'

    url = f'https://{bucket_name}.s3.amazonaws.com/{object_key}'

    try:
        # Send a GET request to retrieve the settings JSON
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            settings = json.loads(response.text)
            return settings
        else:
            print(f'Error retrieving settings: {response.status_code}')
            return None

    except Exception as e:
        print(f'Error retrieving settings: {e}')
        return None


PIXEL_STATES = {}


def debounce(pixel, target_pixel_color):
    if SETTINGS['debounce'] == 0 or pixel not in PIXEL_STATES:
        # Immediately update the pixel color to the target color
        PIXEL_STATES[pixel] = target_pixel_color
        return target_pixel_color
    else:
        current_pixel_color = PIXEL_STATES[pixel]
        # Gradually shift the pixel color towards the target color
        new_pixel_color = []
        for i in range(3):
            current_component = current_pixel_color[i]
            target_component = target_pixel_color[i]
            delta = (target_component - current_component) // SETTINGS['debounce']
            new_component = current_component + delta
            new_pixel_color.append(int(new_component))

        PIXEL_STATES[pixel] = tuple(new_pixel_color)
        return tuple(new_pixel_color)


def write_pixels(counter):
    if not SETTINGS:
        return
    if SETTINGS['state'] == 'off':
        np_strip.fill((0, 0, 0))
        np_strip.write()
        return
    palette = PALETTE_FNS[SETTINGS['palette']]
    pattern = PATTERN_FNS[SETTINGS['pattern']]
    for pixel in range(N_PIXELS):
        np_strip[pixel] = debounce(pixel, palette(pattern(counter, pixel)))
    np_strip.show()


counter = 0


def refresh_state():
    global counter
    write_pixels(counter)
    counter = (counter + 1)
    if counter >= 360000:
        counter = 0


def save_settings(requests):
    new_settings = get_settings(requests)
    if new_settings:
        SETTINGS['palette'] = new_settings.get('palette', 'rainbow')
        SETTINGS['pattern'] = new_settings.get('pattern', 'slide')
        SETTINGS['debounce'] = new_settings.get('debounce', 5)


# def main():
#     requests = wifi_connect()
#     save_settings(requests)
#     n_loops = 0
#     while True:
#         n_loops += 1
#         time.sleep(LOOP_TIME)
#         refresh_state()
#         if n_loops >= N_LOOPS_BETWEEN_CHECKS:
#             save_settings(requests)
#             n_loops = 0
#
# main()

print(f"Starting server on {wifi.radio.ipv4_address}")
server.start(str(wifi.radio.ipv4_address))


async def handle_http_requests():
    try:
        while True:
            # Process any waiting requests
            pool_result = server.poll()
            if pool_result == REQUEST_HANDLED_RESPONSE_SENT:
                # Do something only after handling a request
                print("Request handled")
            await asyncio.sleep(0)
    except Exception as e:
        print('Resetting: ', e)
        microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
        microcontroller.reset()


async def animate_neopixels():
    try:
        while True:
            refresh_state()
            await asyncio.sleep(LOOP_TIME)
    except Exception as e:
        print('Resetting: ', e)
        microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
        microcontroller.reset()


async def main():
    await asyncio.gather(
        asyncio.create_task(handle_http_requests()),
        asyncio.create_task(animate_neopixels())
    )

asyncio.run(main())