from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import datetime
import tkinter as tk
from tkinter import messagebox
import threading
import pandas as pd
import tkinter as tk
from tkinter import ttk

# Hilfsfunktion, um Leerzeichen in einem String durch '-' zu ersetzen
def check_string(product):
    return product.replace(' ', '-')

class WebScraper:
    def __init__(self):
        self.driver = None
        self.actions = None

    def start(self):
        self.driver = webdriver.Chrome()
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

    @staticmethod
    def replace_today_and_yesterday(date_string):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        date_string = date_string.replace('Heute', today.strftime('%d.%m.%Y'))
        date_string = date_string.replace('Gestern', yesterday.strftime('%d.%m.%Y'))

        return date_string

    def __init__(self, product):
        super().__init__()
        self.product = check_string(product)
        self.json_write = JsonWriter('data.json')

    def get_product_url(self):
        self.load_url(f"https://www.kleinanzeigen.de/s-{self.product}/k0")

    def get_product_url_pricerange(self, min_price, max_price):
        self.load_url(f"https://www.kleinanzeigen.de/s-preis:{min_price}:{max_price}/nintendo-switch-lite/k0")

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
                upload = self.replace_today_and_yesterday(upload)
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
def run_scraper():
    product = product_entry.get()
    min_price = min_price_entry.get()
    max_price = max_price_entry.get()

    # Einige grundlegende Eingabevalidierungen
    if not product:
        messagebox.showerror("Fehler", "Bitte Produktname eingeben.")
        return
    if not min_price.isdigit() or not max_price.isdigit():
        messagebox.showerror("Fehler", "Preise müssen numerische Werte sein.")
        return

    status_text.set('Scraper gestartet ...')
    scraper = ProductScraper(product)
    scraper.start()
    scraper.get_product_url_pricerange(min_price, max_price)
    scraper.accept_cookies()
    scraper.get_elements_list_from_html()
    status_text.set('Scraper beendet.')
    status_text.set('Scraper beendet. Statistiken berechnen...')
    min_price, max_price, median_price = calculate_statistics('data.json')
    status_text.set(f'Min Preis: {min_price}, Max Preis: {max_price}, Median Preis: {median_price}')

def start_scraper_thread():
    scraper_thread = threading.Thread(target=run_scraper)
    scraper_thread.start()

def calculate_statistics(filename):
    # JSON-Datei laden und in DataFrame umwandeln
    with open(filename, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    # Preisdaten bereinigen und in numerisches Format umwandeln
    df['price'] = df['price'].str.replace(' €', '').str.replace(' VB', '').str.replace(',', '.').astype(float)

    # Berechnungen durchführen
    min_price = df['price'].min()
    min_product = df.loc[df['price'] == min_price].iloc[0].to_dict()
    max_price = df['price'].max()
    max_product = df.loc[df['price'] == max_price].iloc[0].to_dict()
    median_price = df['price'].median()

    return min_price, min_product, max_price, max_product, median_price

def calculate_and_display_statistics():
    min_price, min_product, max_price, max_product, median_price = calculate_statistics('data.json')
    min_price_text.set(f'Min Preis: {min_price}, Produkt: {min_product}')
    max_price_text.set(f'Max Preis: {max_price}, Produkt: {max_product}')
    median_price_text.set(f'Median Preis: {median_price}')

root = tk.Tk()
root.title("Web Scraper")

notebook = ttk.Notebook(root)

# Erster Tab
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text='Scraper')

product_label = tk.Label(tab1, text="Produkt:")
product_label.grid(row=0, column=0, padx=(20, 10), pady=(20, 10))
product_entry = tk.Entry(tab1)
product_entry.grid(row=0, column=1, padx=(10, 20), pady=(20, 10))

min_price_label = tk.Label(tab1, text="Minimaler Preis:")
min_price_label.grid(row=1, column=0, padx=(20, 10), pady=(10, 10))
min_price_entry = tk.Entry(tab1)
min_price_entry.grid(row=1, column=1, padx=(10, 20), pady=(10, 10))

max_price_label = tk.Label(tab1, text="Maximaler Preis:")
max_price_label.grid(row=2, column=0, padx=(20, 10), pady=(10, 20))
max_price_entry = tk.Entry(tab1)
max_price_entry.grid(row=2, column=1, padx=(10, 20), pady=(10, 20))

status_text = tk.StringVar()
status_label = tk.Label(tab1, textvariable=status_text)
status_label.grid(row=3, column=0, columnspan=2)

submit_button = tk.Button(tab1, text="Suche starten", command=start_scraper_thread)
submit_button.grid(row=4, column=0, columnspan=2, pady=(10, 20))

# Zweiter Tab
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text='Statistik')

calculate_button = tk.Button(tab2, text="Statistiken berechnen", command=calculate_and_display_statistics)
calculate_button.pack(padx=20, pady=(20, 10))

min_price_text = tk.StringVar()
min_price_label = tk.Label(tab2, textvariable=min_price_text)
min_price_label.pack(padx=20, pady=(10, 10))

max_price_text = tk.StringVar()
max_price_label = tk.Label(tab2, textvariable=max_price_text)
max_price_label.pack(padx=20, pady=(10, 10))

median_price_text = tk.StringVar()
median_price_label = tk.Label(tab2, textvariable=median_price_text)
median_price_label.pack(padx=20, pady=(10, 20))

notebook.pack(expand=True, fill='both')

root.mainloop()