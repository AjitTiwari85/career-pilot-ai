from pathlib import Path

from config.config import HEADLESS
from browser.browser_manager import BrowserManager
from linkedin.login import LinkedInLogin
from linkedin.profile import LinkedInProfile
from utils.logger import logger


def main():

    browser = BrowserManager(headless=HEADLESS)

    try:

        logger.info("===== CareerPilot-AI Started =====")

        browser.start()

        logger.info("Browser Started")

        login = LinkedInLogin(browser)
        profile = LinkedInProfile(browser)

        auth = Path("auth/auth.json")

        login.open()

        if not auth.exists():

            input("Login complete hone ke baad ENTER dabao...")

            browser.save_session()

        profile.open()

        logger.info(f"Title : {browser.get_title()}")
        logger.info(f"URL   : {browser.get_url()}")

        profile.screenshot()

    except Exception:

        logger.exception("Unexpected Error")

    finally:

        browser.close()

        logger.info("Browser Closed")

        logger.info("===== CareerPilot-AI Finished =====")


if __name__ == "__main__":
    main()