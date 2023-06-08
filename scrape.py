import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
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

    def check_string(self, product):
        result = ''
        for char in product:
            if char == " ":
                result += '-'
            else:
                result += char
        return result


    def start(self):
        self.driver = uc.Chrome(executable_path=r'drivers/chromedriver.exe', version_main=97)
        self.actions = ActionChains(self.driver)

    def get_product_url(self, product):
        self.get_url(f"https://www.kleinanzeigen.de/s-{product}/k0")
        self.driver.implicitly_wait(30)
        time.sleep(10)
    
    def accept_cookies(self):
        cookies_accept = self.driver.find_element(By.XPATH, '//*[@id="gdpr-banner-accept"]')
        self.actions.click(cookies_accept).perform()

    def get_elements_list_from_html(self):
        elements_list = self.driver.find_element(By.XPATH, "//*[@id='srchrslt-content']")
        items = elements_list.find_elements(By.XPATH, '//*[@id="srchrslt-adtable"]/li/article')
        self.get_items(items)

    def get_items(self, items):
        for item in items:
                title = item.find_element(By.TAG_NAME, 'h2').text
                price = 'no pricing'
                location = 'no location'
                link = 'no link'
                upload = 'no time'
                try:
                    price = item.find_element(By.CLASS_NAME, "aditem-main--middle--price-shipping--price").text
                except:
                    pass
                try:
                    location = item.find_element(By.CLASS_NAME, 'aditem-main--top--left').text
                except:
                    pass
                try:
                    link = item.find_element(By.TAG_NAME, 'a').get_attribute("href")
                except:
                    pass
                try:
                    upload = item.find_element(By.CLASS_NAME, 'aditem-main--top--right').text
                except:
                    pass
                print('TITEL: ', title)
                print('PREIS: ', price)
                print('ORT: ', location)
                print('LINK: ', link)
                print('UPLOAD: ', upload)
                print('TITEL: ', title)
                print('PREIS: ', price)
                print('ORT: ', location)
                print('LINK: ', link)
                print('UPLOAD: ', upload)
    
    def write_json(new_data, filename='data.json'):
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            file_data.append(new_data)
            file.seek(0)
            json.dump(file_data, file, indent=4)

# Erstelle eine Instanz von SeleniumBrowser
product = input("Wonach möchten Sie suchen: ")
browser = SeleniumBrowser(product)
product = browser.check_string(product)  # Save the result of check_string
browser.start()
browser.get_product_url(product)
browser.accept_cookies()
browser.get_elements_list_from_html()
browser.get_items_from_elements_list()