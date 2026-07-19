from utils.logger import logger


class LinkedInProfile:

    # "/in/me/" is a LinkedIn redirect shortcut — it briefly passes through
    # the home feed before resolving to the real profile URL, causing a
    # visible "feed flash". Using the direct profile URL skips that redirect
    # chain entirely.
    #
    # Set this to your actual profile URL. If left as None, falls back to
    # the "/in/me/" shortcut (slower, shows the brief feed flash).
    DIRECT_PROFILE_URL = "https://www.linkedin.com/in/ajittiwari85/"

    def __init__(self, browser):
        self.browser = browser

    def open(self):

        logger.info("Opening Profile")

        url = self.DIRECT_PROFILE_URL or "https://www.linkedin.com/in/me/"

        self.browser.open(url)

        self.browser.wait(3000)

        logger.success("Profile Opened")

    def screenshot(self):

        self.browser.take_screenshot("linkedin-profile")

        logger.success("Profile Screenshot Saved")