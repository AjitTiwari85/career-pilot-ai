from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


def _get_bool(key, default=False):
    value = os.getenv(key)
    if value is None:
        return default
    return value.strip().lower() in ("true", "1", "yes")


# -----------------------
# Browser
# -----------------------

HEADLESS = _get_bool("HEADLESS", default=False)

# -----------------------
# Job Search
# -----------------------

KEYWORD = os.getenv("KEYWORD", "Python Developer")
LOCATION = os.getenv("LOCATION", "")
RESUME_PATH = os.getenv("RESUME_PATH", "")

# -----------------------
# Filters
# Valid values match linkedin/filters.py's ID maps exactly:
#   DATE_POSTED : "Any time" | "Past month" | "Past week" | "Past 24 hours"
#   EXPERIENCE  : "0-1" | "0-2" | "1-3" | "2-5" | "5-10" | "10+"
#                 (or a direct label like "Entry level")
#   REMOTE      : "On-site" | "Remote" | "Hybrid"
#   SORT_BY     : "Most recent" | "Most relevant"
# -----------------------

DATE_POSTED = os.getenv("DATE_POSTED", "Past week")
EXPERIENCE = os.getenv("EXPERIENCE", "0-2")
REMOTE = os.getenv("REMOTE", "Remote")
EASY_APPLY = _get_bool("EASY_APPLY", default=True)
SORT_BY = os.getenv("SORT_BY", "Most recent")

# -----------------------
# Scraper
# -----------------------

SCRAPE_LIMIT = int(os.getenv("SCRAPE_LIMIT", "25"))
JOBS_CSV_PATH = os.getenv("JOBS_CSV_PATH", "data/jobs.csv")
JOBS_JSON_PATH = os.getenv("JOBS_JSON_PATH", "data/jobs.json")