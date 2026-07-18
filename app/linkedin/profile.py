from utils.logger import logger


class LinkedInProfile:

    def __init__(self, browser):
        self.browser = browser

    def open(self):

        logger.info("Opening Profile")

        self.browser.open("https://www.linkedin.com/in/me/")

        self.browser.wait(3000)

        logger.success("Profile Opened")

    def screenshot(self):

        self.browser.take_screenshot("linkedin-profile")

        logger.success("Profile Screenshot Saved")