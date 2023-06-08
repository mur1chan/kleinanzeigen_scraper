import undetected_chromedriver.v2 as uc
from selenium.webdriver import Chrome
import time

class Browser:
    def __init__(self):
        self.driver = None

    def start(self):
        raise NotImplementedError("Must be implemented by subclass")

    def get_url(self, url):
        if not self.driver:
            raise Exception("Browser not started")
        self.driver.get(url)

class SeleniumBrowser(Browser):
    def __init__(self, product):
        super().__init__()
        self.product = product

    def start(self):
        self.driver = uc.Chrome(executable_path=r'drivers/chromedriver.exe', version_main=97)

    def get_product_url(self):
        self.get_url(f"https://www.kleinanzeigen.de/s-{self.product}/k0")

# Erstelle eine Instanz von SeleniumBrowser
browser = SeleniumBrowser(input("Wonach möchten Sie suchen: "))
browser.start()
browser.get_product_url()