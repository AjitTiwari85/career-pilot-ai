from pathlib import Path
from playwright.sync_api import sync_playwright
from utils.logger import logger


class BrowserManager:

    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless
        )

        auth_file = Path("auth/auth.json")

        # Session Exists
        if auth_file.exists() and auth_file.stat().st_size > 0:

            logger.info("✓ Saved LinkedIn session found")

            self.context = self.browser.new_context(
                storage_state=str(auth_file)
            )

        else:

            logger.warning("No saved session found")
            logger.info("Manual login required")

            self.context = self.browser.new_context()

        self.page = self.context.new_page()

    # -----------------------
    # Navigation
    # -----------------------

    def open(self, url, timeout=60000, retries=2):
        """
        Navigates to a URL.

        LinkedIn is a heavy single-page app with constant background network
        activity (analytics, chat widgets, presence pings), so Playwright's
        default wait_until="load" can time out even though the page is
        actually usable. We wait for "domcontentloaded" instead (fires much
        sooner and is enough for our selectors to work), use a longer
        timeout, and retry on failure in case of a transient network hiccup.
        """

        last_error = None

        for attempt in range(1, retries + 2):  # e.g. retries=2 -> 3 total attempts

            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                return

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Navigation to '{url}' failed on attempt {attempt} "
                    f"(wait_until=domcontentloaded): {e}"
                )

                if attempt <= retries:
                    logger.info("Retrying navigation...")
                    self.wait(2000)

        # All attempts failed — try one last time with the loosest possible
        # wait condition ("commit": just wait for the network request to be
        # sent), so at least a partially-loaded page is available for
        # debugging (screenshot, etc.) instead of a hard crash.
        try:
            logger.warning(
                "All domcontentloaded attempts failed. Trying wait_until='commit' as last resort..."
            )
            self.page.goto(url, wait_until="commit", timeout=timeout)
            return
        except Exception as e:
            logger.error(f"Navigation to '{url}' failed completely: {e}")
            raise last_error

    # -----------------------
    # Google Search
    # -----------------------

    def search_google(self, text):

        search_box = self.page.locator('textarea[name="q"]')

        search_box.fill(text)

        search_box.press("Enter")

    # -----------------------
    # Wait
    # -----------------------

    def wait(self, milliseconds):
        self.page.wait_for_timeout(milliseconds)

    # -----------------------
    # Get Title
    # -----------------------

    def get_title(self):
        return self.page.title()

    # -----------------------
    # Get URL
    # -----------------------

    def get_url(self):
        return self.page.url

    # -----------------------
    # Screenshot
    # -----------------------

    def take_screenshot(self, name):

        Path("screenshots").mkdir(exist_ok=True)

        self.page.screenshot(
            path=f"screenshots/{name}.png",
            full_page=True
        )

    # -----------------------
    # Save Session
    # -----------------------

    def save_session(self):

        Path("auth").mkdir(exist_ok=True)

        self.context.storage_state(
            path="auth/auth.json"
        )

        logger.success("✓ Session Saved Successfully")

    # -----------------------
    # Close Browser
    # -----------------------

    def close(self):

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()