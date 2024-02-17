import machine
import time

import neopixel
import uasyncio as asyncio

pixels = 7
np = neopixel.NeoPixel(machine.Pin(16), 7)
color_names_to_rgb = {
    "red": (255, 0, 0),
    "orange": (255, 127, 0),
    "yellow": (255, 255, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "indigo": (75, 0, 130),
    "violet": (148, 0, 211)
}


def adjust_brightness(color, brightness_factor):
    return tuple(int(c * brightness_factor) for c in color)


async def set_all_pixels_to_color(color_name, brightness):

    rgb = color_names_to_rgb[color_name]
    color = adjust_brightness(rgb, brightness)
    for i in range(pixels):
        np[i] = color
    np.write()


async def turn_off_pixels():

    for i in range(pixels):
        np[i] = (0, 0, 0)
    np.write()


if __name__ == "__main__":
    asyncio.run(set_all_pixels_to_color('red', .1))
    # Set the brightness to 0.5 and the color to Red.

    pass
    # asyncio.run(main())
