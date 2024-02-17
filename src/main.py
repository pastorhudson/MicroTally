import argparse
import asyncio
from utils import setup_logger, check_config, ConfigError
import logging


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

    loop = asyncio.get_event_loop()

    try:
        logger.info("Checking Config")
        check_config()
        logger.info('Starting MicroTally')
        from tally_server import run_tallys, cleanup
        loop.run_until_complete(run_tallys(logger))

    except KeyboardInterrupt:
        loop.run_until_complete(cleanup(logger))
        loop.close()
        logger.info("Thanks for using this recipe. Check out more recipes at https://pcochef.com")

    except ConfigError as e:
        logger.error(e)


if __name__ == "__main__":
    main()
