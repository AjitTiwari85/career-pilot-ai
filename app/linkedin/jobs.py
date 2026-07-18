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


from utils.logger import logger


class LinkedInJobs:

    def __init__(self, browser):
        self.browser = browser

    def open(self):

        logger.info("Opening Jobs")

        self.browser.open(
            "https://www.linkedin.com/jobs/search/"
        )

        self.browser.wait(5000)

        logger.success("Jobs Opened")


    def search(self, keyword):

        logger.info(f"Searching : {keyword}")

        search_box = self.browser.page.locator(
            'input[aria-label="Search by title, skill, or company"]'
        ).first

        logger.info(f"Search boxes found: {search_box.count()}")


        
        search_box.fill(keyword)

        search_box.press("Enter")

        self.browser.take_screenshot("jobs-page")

        self.browser.wait(50000)

        logger.success("Search Completed")