import undetected_chromedriver.v2 as uc
from selenium.webdriver import Chrome
import time

class Selenium:
    def __init__(self):
        self.driver = None

    def start_browser(self):
        self.driver = uc.Chrome(executable_path=r'drivers/chromedriver.exe', version_main=97)
        self.driver.get("https://google.de")
        time.sleep(99999)

# Erstelle eine Instanz von uc.Chrome


selenium = Selenium()
selenium.start_browser()
