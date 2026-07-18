from pathlib import Path

from config.config import HEADLESS
from browser.browser_manager import BrowserManager
from utils.logger import logger


def main():

    browser = BrowserManager(headless=HEADLESS)

    try:

        logger.info("===== CareerPilot-AI Started =====")

        browser.start()
        logger.info("Browser Started")

        browser.open("https://www.linkedin.com")
        logger.info("LinkedIn Opened")

        auth = Path("auth/auth.json")

        if not auth.exists():

            logger.warning("No saved session found")
            input("Login complete hone ke baad ENTER dabao...")

            browser.save_session()

        browser.open("https://www.linkedin.com/in/me/")
        logger.info("Profile Opened")

        browser.wait(3000)

        logger.info(f"Title : {browser.get_title()}")
        logger.info(f"URL   : {browser.get_url()}")

        browser.take_screenshot("linkedin-profile")
        logger.success("Screenshot Saved")

    except Exception as e:

        logger.exception(f"Error : {e}")

    finally:

        browser.close()
        logger.info("Browser Closed")
        logger.info("===== CareerPilot-AI Finished =====")


if __name__ == "__main__":
    main()