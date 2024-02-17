import network
import ubinascii


def get_mac():
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    return mac
