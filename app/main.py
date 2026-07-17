from config.config import HEADLESS
from browser.browser_manager import BrowserManager
from utils.logger import logger
import time



def main():

    logger.info("Application started")

    browser = BrowserManager(headless=HEADLESS)

    browser.start()

    logger.info("Browser Started")

    browser.open("https://www.google.com")

    logger.info("Google Opened")

    print(browser.get_title())

    time.sleep(5)

    browser.close()

    logger.info("Browser closed")

    logger.info("Application finished")

if __name__ == "__main__":
    main()