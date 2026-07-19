from pathlib import Path

from config.config import HEADLESS
from browser.browser_manager import BrowserManager
from linkedin.login import LinkedInLogin
from linkedin.profile import LinkedInProfile
from linkedin.jobs import LinkedInJobs
from linkedin.filters import LinkedInFilters
from utils.logger import logger


def main():

    browser = BrowserManager(headless=HEADLESS)

    try:

        logger.info("===== CareerPilot-AI Started =====")

        browser.start()

        logger.info("Browser Started")

        login = LinkedInLogin(browser)
        profile = LinkedInProfile(browser)
        jobs = LinkedInJobs(browser)
        filters = LinkedInFilters(browser)

        auth = Path("auth/auth.json")

        login.open()

        if not auth.exists():
 
            # No saved session yet — must open the feed/home page for manual login
            login.open()
 
            input("Login complete hone ke baad ENTER dabao...")
 
            browser.save_session()
 
        else:
 
            # Saved session already exists — skip the feed entirely,
            # go straight to Profile/Jobs (avoids the "same feed post" issue
            # and saves a page load).
            logger.info("Skipping LinkedIn feed (saved session found).")

        profile.open()

        logger.info(f"Title : {browser.get_title()}")
        logger.info(f"URL   : {browser.get_url()}")

        profile.screenshot()

        jobs.open()

        jobs.search("Python Developer")

        # -----------------------
        # Apply Filters (all in one "All filters" panel session)
        # -----------------------

        filters.apply_filters(
            date_posted="Past week",
            experience="0-2",
            remote="Remote",
            easy_apply=True,
            sort_by="Most recent",
        )

        browser.take_screenshot("jobs-filtered")

    except Exception:

        logger.exception("Unexpected Error")

    finally:

        browser.close()

        logger.info("Browser Closed")

        logger.info("===== CareerPilot-AI Finished =====")


if __name__ == "__main__":
    main()