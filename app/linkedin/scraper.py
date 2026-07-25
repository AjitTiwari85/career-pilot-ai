import csv
import json
from datetime import datetime
from pathlib import Path

from utils.logger import logger


class LinkedInScraper:
    """
    Scrapes job cards from the currently open LinkedIn jobs search results
    page (after filters have been applied) and saves the extracted data
    to CSV and/or JSON.

    Design note: the DOM-scraping part (_get_job_cards, _scroll_load_more)
    needs a live browser/page and can't be easily unit tested. The actual
    text -> dict parsing logic is pulled into a separate PURE function
    (_parse_lines_to_job) that takes plain strings and returns a dict, with
    no Playwright dependency — this is what tests/test_scraper.py exercises.
    """

    def __init__(self, browser):
        self.browser = browser

    # -----------------------
    # Step 1 : Locate job cards (resilient, multiple fallback selectors)
    # -----------------------

    def _get_job_cards(self):

        selectors = [
            "ul.jobs-search__results-list > li",
            "div.jobs-search-results-list li[data-occludable-job-id]",
            "li.jobs-search-results__list-item",
            "div[data-job-id]",
        ]

        for selector in selectors:
            cards = self.browser.page.locator(selector)
            if cards.count() > 0:
                logger.info(f"Job cards found using selector: '{selector}' ({cards.count()} cards)")
                return cards

        # Last resort : any <li> containing a job view link
        fallback = self.browser.page.locator("li:has(a[href*='/jobs/view/'])")
        logger.warning(f"Falling back to generic job-link selector ({fallback.count()} cards)")
        return fallback

    # -----------------------
    # Step 2 : Scroll the results list to lazy-load more cards
    # -----------------------

    def _scroll_load_more(self, max_scrolls=8, pause_ms=1000):

        logger.info("Scrolling job list to load more results...")

        last_count = 0

        for i in range(max_scrolls):

            cards = self._get_job_cards()
            current_count = cards.count()

            if current_count == last_count and i > 1:
                logger.info(f"No new cards loaded after scroll {i}. Stopping scroll.")
                break

            last_count = current_count

            try:
                if current_count > 0:
                    cards.last.scroll_into_view_if_needed(timeout=3000)
                else:
                    self.browser.page.mouse.wheel(0, 800)
            except Exception:
                self.browser.page.mouse.wheel(0, 800)

            self.browser.wait(pause_ms)

        final_count = self._get_job_cards().count()
        logger.info(f"Finished scrolling. Total cards available: {final_count}")

    # -----------------------
    # Step 3 : PURE parsing helper (no browser needed -> unit testable)
    # -----------------------

    @staticmethod
    def _parse_lines_to_job(lines, href=""):
        """
        Given the raw visible text lines of a job card (already split and
        stripped) and its link href, returns a clean job dict.

        This is a pure function on purpose: no Playwright objects go in or
        out, so it can be tested directly with plain Python lists/strings.
        """

        lines = [line.strip() for line in lines if line and line.strip()]

        title = lines[0] if len(lines) > 0 else ""
        company = lines[1] if len(lines) > 1 else ""
        location = lines[2] if len(lines) > 2 else ""

        posted = next(
            (
                line for line in lines
                if any(kw in line.lower() for kw in ["ago", "hour", "day", "week", "month"])
            ),
            "",
        )

        easy_apply = any("easy apply" in line.lower() for line in lines)

        return {
            "title": title,
            "company": company,
            "location": location,
            "link": href,
            "posted": posted,
            "easy_apply": easy_apply,
        }

    # -----------------------
    # Step 4 : Extract one job dict from a live card locator
    # -----------------------

    def _extract_job_from_card(self, card):

        try:
            link_el = card.locator('a[href*="/jobs/view/"]').first

            href = ""
            if link_el.count() > 0:
                href = link_el.get_attribute("href") or ""
                if href.startswith("/"):
                    href = f"https://www.linkedin.com{href}"

            raw_text = card.inner_text(timeout=2000)
            lines = raw_text.split("\n")

            return self._parse_lines_to_job(lines, href)

        except Exception as e:
            logger.warning(f"Failed to extract a job card: {e}")
            return None

    # -----------------------
    # Step 5 : Public entry point
    # -----------------------

    def scrape(self, limit=25, scroll_first=True):

        logger.info(f"Starting job scrape (limit={limit})...")

        if scroll_first:
            self._scroll_load_more()

        cards = self._get_job_cards()
        total = cards.count()

        if total == 0:
            logger.error("No job cards found on the page. Nothing to scrape.")
            return []

        jobs = []
        seen_links = set()

        for i in range(min(total, limit)):

            job = self._extract_job_from_card(cards.nth(i))

            if job is None:
                continue

            if not job["title"]:
                continue

            if job["link"] and job["link"] in seen_links:
                continue

            if job["link"]:
                seen_links.add(job["link"])

            jobs.append(job)

        logger.success(f"Scraped {len(jobs)} unique jobs.")
        return jobs

    # -----------------------
    # Step 6 : Save results
    # -----------------------

    def save_to_csv(self, jobs, filepath="data/jobs.csv"):

        if not jobs:
            logger.warning("No jobs to save (empty list). Skipping CSV write.")
            return

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = ["title", "company", "location", "link", "posted", "easy_apply", "scraped_at"]

        scraped_at = datetime.now().isoformat(timespec="seconds")

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for job in jobs:
                row = dict(job)
                row["scraped_at"] = scraped_at
                writer.writerow(row)

        logger.success(f"Saved {len(jobs)} jobs to CSV : {path}")

    def save_to_json(self, jobs, filepath="data/jobs.json"):

        if not jobs:
            logger.warning("No jobs to save (empty list). Skipping JSON write.")
            return

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        scraped_at = datetime.now().isoformat(timespec="seconds")

        payload = {
            "scraped_at": scraped_at,
            "count": len(jobs),
            "jobs": jobs,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        logger.success(f"Saved {len(jobs)} jobs to JSON : {path}")