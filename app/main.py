from pathlib import Path

from config.config import (
    HEADLESS,
    KEYWORD,
    DATE_POSTED,
    EXPERIENCE,
    REMOTE,
    EASY_APPLY,
    SORT_BY,
    SCRAPE_LIMIT,
    JOBS_CSV_PATH,
    JOBS_JSON_PATH,
)
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

        jobs.search(KEYWORD)

        # -----------------------
        # Apply Filters ONE AT A TIME (each confirms via its own
        # "Show results" click) — more reliable than batching them all
        # in a single panel session.
        # -----------------------

        filters.date_posted(DATE_POSTED)
        filters.experience(EXPERIENCE)
        filters.remote(REMOTE)

        if EASY_APPLY:
            filters.easy_apply()

        filters.sort_by(SORT_BY)

        browser.take_screenshot("jobs-filtered")

        # -----------------------
        # Scrape filtered job results
        # -----------------------

        scraped_jobs = scraper.scrape(limit=SCRAPE_LIMIT)

        scraper.save_to_csv(scraped_jobs, filepath=JOBS_CSV_PATH)
        scraper.save_to_json(scraped_jobs, filepath=JOBS_JSON_PATH)

        logger.info(f"Total jobs scraped: {len(scraped_jobs)}")

    except Exception:

        logger.exception("Unexpected Error")

    finally:

        browser.close()

        logger.info("Browser Closed")

        logger.info("===== CareerPilot-AI Finished =====")


if __name__ == "__main__":
    main()