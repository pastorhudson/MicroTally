import argparse
from utils import setup_logger
from pypco.exceptions import PCORequestException


def main():
    logger = setup_logger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", help="test option: return the string 'SUCCESS'", action='store_true')
    # parser.add_argument("-s", "--service_type_id", help="service type id")
    # parser.add_argument("-p", "--plan_id", help="plan id")

    args = parser.parse_args()

    if args.test:
        print("SUCCESS")
        return
    try:
        print('Hello World')
    except KeyboardInterrupt:
        logger.info("Thanks for using this recipe. Check out more recipes at https://pcochef.com")
    except PCORequestException:
        logger.error("Please Check your Planning Center API keys are correct in the config.ini")


if __name__ == "__main__":
    main()
