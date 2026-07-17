from playwright.sync_api import sync_playwright


class BrowserManager:

    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless
        )

        self.page = self.browser.new_page()

        return self.page
    
    def open(self,url):
        self.page.goto(url)

    def get_title(self):
        return self.page.title()
    
    def get_url(self):
        return self.page.url
    
    # def refresh(self):
    #     self.page.reload()

    def take_screenshot(self, name):
        self.page.screenshot(path=f"screenshots/{name}.png")

    def close(self):

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()