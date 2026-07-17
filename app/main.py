from config.config import HEADLESS
from browser.browser_manager import BrowserManager
from utils.logger import logger
import time


def main():

    browser = BrowserManager(headless=HEADLESS)

    try:

        logger.info("Application Started")

        browser.start()

        logger.info("Browser Started")

        browser.open("https://google.com")

        logger.info("Google Opened")

        browser.take_screenshot("google")

        logger.info(f"Title : {browser.get_title()}")

        logger.info(f"URL : {browser.get_url()}")

        time.sleep(5)

    except Exception as e:

        logger.error(f"Error : {e}")

    finally:

        browser.close()

        logger.info("Browser Closed")

        logger.info("Application Finished")


if __name__ == "__main__":
    main()