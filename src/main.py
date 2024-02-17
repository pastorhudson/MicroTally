import argparse
import asyncio

from tally_server import cleanup
from utils import setup_logger, check_config, ConfigError, should_continue
import logging
import win32api
import win32con


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", help="test option: return the string 'SUCCESS'", action='store_true')
    parser.add_argument("-l", "--loglevel", help="Set log level info(default) or debug")

    args = parser.parse_args()

    if args.loglevel:
        if args.loglevel == 'debug':
            logger = setup_logger('microtally', logging.DEBUG)
        if args.loglevel == 'info':
            logger = setup_logger('microtally', logging.INFO)
    else:
        logger = setup_logger('microtally')

    if args.test:
        logger.info("SUCCESS!")
        return

    global loop

    try:
        logger.info("Checking Config")
        check_config()
        logger.info('Starting MicroTally')
        from tally_server import run_tallys, cleanup
        loop.run_until_complete(run_tallys(logger))

    except KeyboardInterrupt:

        logger.info("Thanks for using this recipe. Check out more recipes at https://pcochef.com")

    except ConfigError as e:
        logger.error(e)


def console_ctrl_handler(ctrl_type):
    global should_continue
    global loop

    if ctrl_type in [win32con.CTRL_C_EVENT, win32con.CTRL_BREAK_EVENT, win32con.CTRL_CLOSE_EVENT]:
        print("Stopping loop...")
        # Ensure cleanup() is called to create a coroutine object
        coroutine = cleanup()  # Assuming cleanup is a coroutine function and doesn't require arguments
        # Now pass the coroutine object to run_coroutine_threadsafe
        asyncio.run_coroutine_threadsafe(coroutine, loop)
        return True  # Indicate that the handler handled the event
    return False  # Event was not handled


win32api.SetConsoleCtrlHandler(console_ctrl_handler, True)

if __name__ == "__main__":
    global loop
    loop = asyncio.get_event_loop()

    main()
