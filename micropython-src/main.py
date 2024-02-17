import uasyncio as asyncio
import wifimgr
import machine

from light_rotate import do_connection_status
from tally_control import set_all_pixels_to_color, turn_off_pixels
from utils import get_mac
import status

try:
    import usocket as socket
except ImportError:
    import socket

led = machine.Pin(15, machine.Pin.OUT)


def webpage(filename, led_state):
    # Open the HTML file and read its content asynchronously
    with open(filename, 'r') as html_file:
        html_content = html_file.read()

    html_content = html_content.replace('[LED State]', f"[{str(led_state)}]").replace('[MAC]', get_mac())
    return html_content


async def handle_connection(reader, writer):
    status.WIFI_STATUS = 'running'
    await turn_off_pixels()

    # addr = writer.get_extra_info('peername')
    # print('Got a connection from %s' % str(addr))
    query_params = {'led': 'off'}
    request_bytes = await reader.read(1024)
    request = request_bytes.decode('utf-8')  # Decode bytes to string using UTF-8
    print('Content = %s' % request)
    # Print the entire request for debugging
    print('Full Request:\n%s' % request)

    # Extract the request line (first line)
    request_line = request.split('\r\n')[0]
    print('Request Line: %s' % request_line)

    # Extract the URL part of the request line
    path = request_line.split(' ')[1]
    print('Path: %s' % path)

    # Optional: Extract the path and query parameters separately
    if '?' in path:
        path, query_string = path.split('?', 1)
        print('Path without query: %s' % path)
        print('Query string: %s' % query_string)
        # Further parsing to extract individual query parameters
        query_params = dict(param.split('=') for param in query_string.split('&'))
        print('Query Parameters: %s' % query_params)
    else:
        query_string = ''

    # Parse request and update LED state
    led_state = "off"
    # Update LED state based on the request
    if query_params['led'] == 'queue':
        led_state = "Queue"
        print('Led State = %s' % led_state)
        await set_all_pixels_to_color('green', .1)
    elif query_params['led'] == 'live':
        led_state = "Live"
        print('Led State = %s' % led_state)
        await set_all_pixels_to_color('red', .1)

    elif query_params['led'] == 'off':
        led_state = "Off"
        print('Led State = %s' % led_state)
        await turn_off_pixels()
    print('done with lights')
    # Respond with the HTML page
    response = webpage('html/tally.html', led_state)
    writer.write('HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n'.encode() + response.encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    pass


async def startup():
    wlan = wifimgr.get_connection()
    if wlan is None:
        print("Could not initialize the network connection.")
        while True:
            pass  # Infinite loop to prevent further execution
    print("ESP OK")
    status.WIFI_STATUS = 'connected'

    # Start the server
    server = await asyncio.start_server(handle_connection, '0.0.0.0', 80)

    print("HTTP server is running")

    try:
        await server.serve_forever()
    except asyncio.CancelledError:
        print("Server was cancelled")
    finally:
        await server.wait_closed()
        print("Server has been closed")


async def main():
    await asyncio.gather(
        startup(),
        do_connection_status(),
    )

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Program interrupted by keyboard")
except Exception as e:
    print(f"Unexpected error: {e}")
