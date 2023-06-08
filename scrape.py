import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import json

# Hilfsfunktion, um Leerzeichen in einem String durch '-' zu ersetzen
def check_string(product):
    return product.replace(' ', '-')

class WebScraper:
    def __init__(self):
        self.driver = None
        self.actions = None

    def start(self):
        self.driver = uc.Chrome(executable_path=r'drivers/chromedriver.exe', version_main=97)
        self.actions = ActionChains(self.driver)

    def load_url(self, url):
        if not self.driver:
            raise Exception("Browser not started")
        self.driver.get(url)
        self.driver.implicitly_wait(30)
        time.sleep(10)

    def find_element(self, xpath):
        return self.driver.find_element(By.XPATH, xpath)

    def quit(self):
        self.driver.close()

class ProductScraper(WebScraper):
    def __init__(self, product):
        super().__init__()
        self.product = check_string(product)
        self.json_write = JsonWriter('data.json')

    def get_product_url(self):
        self.load_url(f"https://www.kleinanzeigen.de/s-{self.product}/k0")

    def accept_cookies(self):
        cookies_accept = self.find_element('//*[@id="gdpr-banner-accept"]')
        self.actions.click(cookies_accept).perform()

    def get_elements_list_from_html(self):
        elements_list = self.find_element("//*[@id='srchrslt-content']")
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
            scraped_data = {
            'title': title,
            'price': price,
            'location': location,
            'link': link,
            'upload': upload
            }
            self.json_write.write_data(scraped_data)
        print("Die Inhalte wurden gespeichert.")
        self.quit()

class DataWriter:
    def __init__(self, filename):
        self.filename = filename

    def write_data(self, data):
        raise NotImplementedError("Must be implemented by subclass")

class JsonWriter(DataWriter):
    def write_data(self, new_data):
        try:
            with open(self.filename, 'r+') as file:
                file_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            file_data = []
        
        file_data.append(new_data)
        
        with open(self.filename, 'w') as file:
            json.dump(file_data, file, indent=4)

# Erstelle eine Instanz von ProductScraper
product = input("Wonach möchten Sie suchen: ")
scraper = ProductScraper(product)
scraper.start()
scraper.get_product_url()
scraper.accept_cookies()
scraper.get_elements_list_from_html()
