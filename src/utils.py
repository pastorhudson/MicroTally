import configparser
import os
import logging
import colorlog
from datetime import datetime
from wirecastCOMAPI import PreviewShotID, LiveShotID, getName


def setup_logger(logger_name):
    # Create a logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Create a color formatter for the console
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    # Create a console handler and set the color formatter
    ch = logging.StreamHandler()
    ch.setFormatter(color_formatter)

    # Create a file handler and set level to debug
    date = datetime.now().strftime('%Y-%m-%d')
    fh = logging.FileHandler(f'{date}-log.txt')

    # Create a standard formatter for the file
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


logger = setup_logger(__name__)


def check_config():
    # Check if the file does not exist
    if not os.path.isfile('config.ini'):

        # Create a configparser object
        config = configparser.ConfigParser()

        # Populate the configparser object with your data
        config['microtallys'] = {
            ';How many layers do you have in wirecast?': '',
            'wirecast_layers': 2,
            ';Set the name and ip addresses of your microtallys': '',
            'left_cam': '192.168.1.183',
            'left_cam_wirecast_name': 'Left',
            'right_cam': '192.168.1.64',
            'right_cam_wirecast_name': 'Right',
            'center_cam': '192.168.1.52',
            'center_cam_wirecast_name': 'Center',
        }

        # Write the populated configparser object to config.ini file
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        raise Exception("MicroTally configuration not found.\n"
                        "One has been created for you. Please edit the config.ini with your own settings.")
    # logger.info("Config File Found")
    return


def get_microtally_config():
    """
    Returns the IP addresses of the MicroTallys
    configured in the 'config.ini' file.

    :return: A dict of the IP addresses of the MicroTallys.
    """
    check_config()
    config = configparser.ConfigParser()
    config.read('config.ini')

    tally_ip_dict = {}  # initialize an empty dict to store tally_name:ip_address pairs

    for tally_name in config['microtallys']:
        # assuming that each tally_name has an associated ip_address
        ip_address = config['microtallys'][tally_name]
        tally_ip_dict[tally_name] = ip_address
    return tally_ip_dict


def get_wirecast_shots():
    CONFIG = get_microtally_config()
    live_cams = []
    queued_cams = []
    for layer in range(int(CONFIG['wirecast_layers'])):
        layer += 1
        live_cams.append(str(getName(LiveShotID(layer))))
        queued_cams.append(str(getName(PreviewShotID(layer))))

    return {'live_cams': live_cams, 'queued_cams': queued_cams}


if __name__ == '__main__':
    print(get_microtally_config())
    print(get_wirecast_shots())
