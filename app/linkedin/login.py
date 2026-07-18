from utils.logger import logger


class LinkedInLogin:

    def __init__(self, browser):
        self.browser = browser

    def open(self):

        logger.info("Opening LinkedIn")

        self.browser.open("https://www.linkedin.com")

        logger.success("LinkedIn Opened")