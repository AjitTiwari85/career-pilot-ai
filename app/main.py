from pathlib import Path

from config.config import HEADLESS
from browser.browser_manager import BrowserManager
from linkedin.login import LinkedInLogin
from linkedin.profile import LinkedInProfile
from linkedin.jobs import LinkedInJobs
from linkedin.filters import LinkedInFilters
from linkedin.scraper import LinkedInScraper
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
        scraper = LinkedInScraper(browser)

        auth = Path("auth/auth.json")

        if not auth.exists():

            login.open()

            input("Login complete hone ke baad ENTER dabao...")

            browser.save_session()

        else:

            logger.info("Skipping LinkedIn feed (saved session found).")

        profile.open()

        logger.info(f"Title : {browser.get_title()}")
        logger.info(f"URL   : {browser.get_url()}")

        profile.screenshot()

        jobs.open()

        jobs.search("Python Developer")

        # -----------------------
        # Apply Filters ONE AT A TIME (each confirms via its own
        # "Show results" click). LinkedIn's panel resets earlier
        # selections during rapid batched clicks without an intermediate
        # confirm, so sequential calls are more reliable than apply_filters().
        # -----------------------

        filters.date_posted("Past week")
        filters.experience("0-2")
        filters.remote("Remote")
        filters.easy_apply()
        filters.sort_by("Most recent")

        browser.take_screenshot("jobs-filtered")

        # -----------------------
        # Scrape filtered job results
        # -----------------------

        scraped_jobs = scraper.scrape(limit=25)

        scraper.save_to_csv(scraped_jobs, filepath="data/jobs.csv")
        scraper.save_to_json(scraped_jobs, filepath="data/jobs.json")

        logger.info(f"Total jobs scraped: {len(scraped_jobs)}")

    except Exception:

        logger.exception("Unexpected Error")

    finally:

        browser.close()

        logger.info("Browser Closed")

        logger.info("===== CareerPilot-AI Finished =====")


if __name__ == "__main__":
    main()