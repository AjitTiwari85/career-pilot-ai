from config.config import HEADLESS
from browser.browser_manager import BrowserManager
import time



def main():

    browser = BrowserManager(headless=HEADLESS)

    page = browser.start()

    page.goto("https://www.google.com")

    print("Title :" , browser.get_title())

    print("URL :" , browser.get_url())

    time.sleep(5)

    browser.close()

if __name__ == "__main__":
    main()