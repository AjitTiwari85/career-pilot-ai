"""
Unit tests for LinkedInScraper.

These tests do NOT open a real browser. They test:
  1. _parse_lines_to_job() - pure text -> dict parsing logic
  2. save_to_csv() / save_to_json() - file writing logic

Run with:
    pytest tests/test_scraper.py -v

Setup note:
    This file expects the project's `app/` folder to be importable.
    If you get "ModuleNotFoundError: No module named 'linkedin'",
    make sure a `tests/conftest.py` exists (see bottom of this file
    for the one-line content it needs) OR run pytest from inside `app/`.
"""

import sys
import os
import csv
import json

import pytest

# Make sure `app/` is on sys.path so `from linkedin.scraper import ...` works
# regardless of which directory pytest is invoked from.
APP_DIR = os.path.join(os.path.dirname(__file__), "..", "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from linkedin.scraper import LinkedInScraper  # noqa: E402


# =====================================================
# Tests for _parse_lines_to_job (pure function, no browser needed)
# =====================================================

class TestParseLinesToJob:

    def test_basic_job_card(self):

        lines = [
            "Senior Python Engineer | $27/hr Remote",
            "Crossing Hurdles",
            "India (Remote)",
            "Reposted 10 hours ago",
            "Over 100 applicants",
            "Easy Apply",
        ]

        job = LinkedInScraper._parse_lines_to_job(lines, href="https://www.linkedin.com/jobs/view/12345")

        assert job["title"] == "Senior Python Engineer | $27/hr Remote"
        assert job["company"] == "Crossing Hurdles"
        assert job["location"] == "India (Remote)"
        assert job["link"] == "https://www.linkedin.com/jobs/view/12345"
        assert "10 hours ago" in job["posted"]
        assert job["easy_apply"] is True

    def test_job_card_without_easy_apply(self):

        lines = [
            "Backend Software Developer (Remote)",
            "Hire Feed",
            "India (Remote)",
            "Promoted",
        ]

        job = LinkedInScraper._parse_lines_to_job(lines, href="https://www.linkedin.com/jobs/view/999")

        assert job["title"] == "Backend Software Developer (Remote)"
        assert job["company"] == "Hire Feed"
        assert job["easy_apply"] is False

    def test_empty_lines_are_filtered_out(self):

        lines = ["", "  ", "Python Developer Intern", "", "Zenithbyte", "India (Remote)"]

        job = LinkedInScraper._parse_lines_to_job(lines, href="")

        assert job["title"] == "Python Developer Intern"
        assert job["company"] == "Zenithbyte"
        assert job["location"] == "India (Remote)"

    def test_missing_fields_default_to_empty_string(self):

        job = LinkedInScraper._parse_lines_to_job([], href="")

        assert job["title"] == ""
        assert job["company"] == ""
        assert job["location"] == ""
        assert job["posted"] == ""
        assert job["easy_apply"] is False

    def test_only_title_present(self):

        job = LinkedInScraper._parse_lines_to_job(["Just A Title"], href="https://x.com/1")

        assert job["title"] == "Just A Title"
        assert job["company"] == ""
        assert job["location"] == ""

    def test_posted_time_detection_variants(self):

        for keyword_line in ["Posted 2 days ago", "1 week ago", "Reposted 3 hours ago", "Posted last month"]:
            lines = ["Some Title", "Some Co", "Some Location", keyword_line]
            job = LinkedInScraper._parse_lines_to_job(lines, href="")
            assert job["posted"] == keyword_line, f"Failed to detect posted time in: '{keyword_line}'"

    def test_easy_apply_case_insensitive(self):

        lines = ["Title", "Company", "Location", "easy apply"]

        job = LinkedInScraper._parse_lines_to_job(lines, href="")

        assert job["easy_apply"] is True


# =====================================================
# Tests for save_to_csv / save_to_json (real file I/O, using tmp_path)
# =====================================================

class TestSaveOutputs:

    SAMPLE_JOBS = [
        {
            "title": "Python Developer",
            "company": "Acme Corp",
            "location": "India (Remote)",
            "link": "https://www.linkedin.com/jobs/view/1",
            "posted": "1 day ago",
            "easy_apply": True,
        },
        {
            "title": "Backend Engineer",
            "company": "Beta Inc",
            "location": "Noida, India",
            "link": "https://www.linkedin.com/jobs/view/2",
            "posted": "3 hours ago",
            "easy_apply": False,
        },
    ]

    def test_save_to_csv_creates_file_with_correct_rows(self, tmp_path):

        scraper = LinkedInScraper(browser=None)  # no browser needed for saving
        out_file = tmp_path / "jobs.csv"

        scraper.save_to_csv(self.SAMPLE_JOBS, filepath=str(out_file))

        assert out_file.exists()

        with open(out_file, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert len(rows) == 2
        assert rows[0]["title"] == "Python Developer"
        assert rows[0]["company"] == "Acme Corp"
        assert rows[1]["title"] == "Backend Engineer"
        assert "scraped_at" in rows[0]  # auto-added timestamp column

    def test_save_to_csv_skips_empty_list(self, tmp_path):

        scraper = LinkedInScraper(browser=None)
        out_file = tmp_path / "jobs.csv"

        scraper.save_to_csv([], filepath=str(out_file))

        assert not out_file.exists()

    def test_save_to_json_creates_valid_json(self, tmp_path):

        scraper = LinkedInScraper(browser=None)
        out_file = tmp_path / "jobs.json"

        scraper.save_to_json(self.SAMPLE_JOBS, filepath=str(out_file))

        assert out_file.exists()

        with open(out_file, encoding="utf-8") as f:
            data = json.load(f)

        assert data["count"] == 2
        assert len(data["jobs"]) == 2
        assert data["jobs"][0]["title"] == "Python Developer"
        assert "scraped_at" in data

    def test_save_to_json_skips_empty_list(self, tmp_path):

        scraper = LinkedInScraper(browser=None)
        out_file = tmp_path / "jobs.json"

        scraper.save_to_json([], filepath=str(out_file))

        assert not out_file.exists()

    def test_save_creates_parent_directory_if_missing(self, tmp_path):

        scraper = LinkedInScraper(browser=None)
        nested_path = tmp_path / "nested" / "dir" / "jobs.csv"

        scraper.save_to_csv(self.SAMPLE_JOBS, filepath=str(nested_path))

        assert nested_path.exists()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))