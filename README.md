# CareerPilot-AI

A resilient browser automation platform built with **Python** and **Playwright** that automates job-search workflows — session-persistent login, multi-criteria filtering, structured data scraping, and safety-first automated form-filling.

Built as a personal deep-dive into browser automation, resilient system design against dynamic single-page applications, and debugging flaky, timing-dependent systems.

---

##  Features

- **Persistent session login** — logs in once, reuses saved session cookies on future runs
- **Resilient filter automation** — applies search filters (date posted, experience level, workplace type, sort order) via a layered fallback-selector system that survives frequent UI changes
- **Structured data scraping** — extracts job title, company, location, posting date, and application link into **CSV** and **JSON**
- **Safe-by-default auto-apply module**
  - Dry-run mode (fills forms but stops before submitting)
  - Per-run application cap
  - Duplicate-application tracking (won't re-apply to the same job across runs)
- **Fully configurable** via `.env` — no code changes needed to adjust search keyword, filters, or limits
- **Tested core logic** — parsing and file-persistence logic covered by `pytest`, decoupled from the browser layer so tests run without a live browser session

---

##  Tech Stack

| Layer | Tools |
|---|---|
| Automation | Python, Playwright |
| Config | python-dotenv |
| Logging | loguru |
| Testing | pytest |

---

##  Project Structure

```
CareerPilot-AI/
├── app/
│   ├── browser/
│   │   └── browser_manager.py     # Browser lifecycle, navigation, session save/load
│   ├── config/
│   │   └── config.py              # .env-driven configuration
│   ├── linkedin/
│   │   ├── login.py                # Login page navigation
│   │   ├── profile.py              # Profile page interaction
│   │   ├── jobs.py                 # Job search navigation
│   │   ├── filters.py              # Resilient filter automation
│   │   ├── scraper.py              # Job data extraction
│   │   └── apply.py                # Safe-by-default auto-apply automation
│   ├── utils/
│   │   └── logger.py               # Centralized logging setup
│   └── main.py                     # Orchestrates the full pipeline
├── tests/
│   └── test_scraper.py            # Unit tests (parsing + file I/O)
├── data/                          # Scraped job output (CSV/JSON)
├── logs/                          # Rotating application logs
├── screenshots/                   # Debug screenshots
├── auth/                          # Saved session state (gitignored)
├── .env                           # Local configuration (gitignored)
├── requirements.txt
└── README.md
```

---

##  Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/AjitTiwari85/CareerPilot-AI.git
cd CareerPilot-AI
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure environment

Copy `.env.example` to `.env` and adjust values:

```env
# Browser
HEADLESS=False

# Job Search
KEYWORD=Python Developer
LOCATION=
RESUME_PATH=

# Filters
DATE_POSTED=Past week
EXPERIENCE=0-2
REMOTE=Remote
EASY_APPLY=True
SORT_BY=Most recent

# Scraper
SCRAPE_LIMIT=25
JOBS_CSV_PATH=data/jobs.csv
JOBS_JSON_PATH=data/jobs.json

# Easy Apply Automation (see Safety Notes below)
DRY_RUN=True
MAX_APPLICATIONS_PER_RUN=5
DEFAULT_TEXT_ANSWER=N/A
DEFAULT_NUMBER_ANSWER=2
APPLIED_LOG_PATH=data/applied_jobs.json
```

### 3. Run

```bash
python app/main.py
```

On first run (no saved session), the browser will open for manual login — complete login, then press Enter in the terminal to save the session for future runs.

### 4. Run tests

```bash
pytest tests/ -v
```

---

##  Configuration Reference

| Variable | Options | Default |
|---|---|---|
| `DATE_POSTED` | `Any time` \| `Past month` \| `Past week` \| `Past 24 hours` | `Past week` |
| `EXPERIENCE` | `0-1` \| `0-2` \| `1-3` \| `2-5` \| `5-10` \| `10+` (or a direct label like `Entry level`) | `0-2` |
| `REMOTE` | `On-site` \| `Remote` \| `Hybrid` | `Remote` |
| `SORT_BY` | `Most recent` \| `Most relevant` | `Most recent` |
| `EASY_APPLY` | `True` \| `False` | `True` |
| `DRY_RUN` | `True` \| `False` | `True` |

---

##  Notable Engineering Challenges

- **Ambiguous text-selectors** — a filter label like "Internship" existed in two different sections of the UI. Fixed by switching from text-matching to unique, DOM-inspected element IDs, eliminating an entire class of similar bugs.
- **Race condition in panel state** — a failed "close panel" action could leave the UI in a state where the next step incorrectly assumed the panel was still fully open, silently skipping re-initialization. Fixed architecturally by batching all selections into a single open/close cycle instead of adding more retries.
- **Testability without a browser** — pure parsing/persistence logic was separated from Playwright-dependent code, enabling fast, reliable unit tests with no live browser dependency.

---

## ⚠️ Safety Notes & Disclaimer

This project was built as a **personal learning project** to explore browser automation, resilient selector design, and debugging flaky systems — not for production or commercial use.

- Automating interactions with third-party platforms may violate their Terms of Service. Use at your own discretion and risk.
- The auto-apply module defaults to **dry-run mode** and should only be disabled after careful verification, since it can submit real applications with auto-filled (potentially generic) answers to real employers.
- Rate limiting and duplicate-application tracking are built in, but this does not guarantee compliance with any platform's automation policies.

---

## 📄 License

See [LICENSE](./LICENSE) for details.
