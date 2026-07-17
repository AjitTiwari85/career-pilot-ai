from config.config import HEADLESS
from browser.browser_manager import BrowserManager



def main():

    browser = BrowserManager(headless=HEADLESS)

    page = browser.start()

    page.goto("https://www.google.com")

    print(page.title())

    browser.close()

if __name__ == "__main__":
    main()