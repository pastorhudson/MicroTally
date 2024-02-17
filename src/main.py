import argparse
import asyncio
import signal
from src.tally_server import signal_handler
from utils import setup_logger, check_config, ConfigError
import logging


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", help="test option: return the string 'SUCCESS'", action='store_true')
    parser.add_argument("-l", "--loglevel", help="Set log level info(default) or debug")
    # parser.add_argument("-p", "--plan_id", help="plan id")

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
    try:
        logger.info("Checking Config")
        check_config()
        logger.info('Starting MicroTally')
        from tally_server import run_tallys
        loop = asyncio.get_event_loop()
        for sig in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(getattr(signal, sig), signal_handler, loop, sig)

        try:
            loop.run_until_complete(run_tallys(logger))
        except (KeyboardInterrupt, RuntimeError):
            pass
        finally:
            loop.close()
            logger.info("Program exited.")

    except ConfigError as e:
        logger.error(e)
    except KeyboardInterrupt:
        logger.info("Thanks for using this recipe. Check out more recipes at https://pcochef.com")


if __name__ == "__main__":
    main()
