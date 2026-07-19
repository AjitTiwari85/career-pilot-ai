# from utils.logger import logger


# class LinkedInJobs:

#     def __init__(self, browser):
#         self.browser = browser

#     def open(self):

#         logger.info("Opening Jobs Page")

#         self.browser.open("https://www.linkedin.com/jobs/")

#         self.browser.wait(3000)

#         logger.success("Jobs Page Opened")

#     def search(self, keyword):

#         logger.info(f"Searching : {keyword}")

#         search_box = self.browser.page.locator(
#             'input[aria-label="Search by title, skill, or company"]'
#         )

#         search_box.fill(keyword)

#         search_box.press("Enter")

#         self.browser.take_screenshot("jobs-page")

#         self.browser.wait(50000)

#         logger.success("Search Completed")


from urllib.parse import quote

from utils.logger import logger


class LinkedInJobs:

    def __init__(self, browser):
        self.browser = browser

    def open(self):

        logger.info("Opening Jobs")

        self.browser.open("https://www.linkedin.com/jobs/search/")

        self.browser.wait(3000)

        logger.success("Jobs Opened")

    def search(self, keyword, location="", sort_by_recent=True):
        """
        Instead of typing into the search box (which can carry over LinkedIn's
        remembered "currentJobId" and default "Most Relevant" sort from a
        previous run), we navigate DIRECTLY to a fully-formed search URL.

        This guarantees a fresh, keyword-matched result set sorted the way
        we want, instead of showing the same cached top job every run.

        sortBy=DD is the same "Most Recent" value used by filters.py's
        panel-based sort (input#advanced-filter-sortBy-DD).
        """

        logger.info(f"Searching : {keyword}")

        params = f"keywords={quote(keyword)}"

        if location:
            params += f"&location={quote(location)}"

        if sort_by_recent:
            params += "&sortBy=DD"

        url = f"https://www.linkedin.com/jobs/search/?{params}"

        self.browser.open(url)

        self.browser.wait(3000)

        self.browser.take_screenshot("jobs-page")

        logger.success("Search Completed")