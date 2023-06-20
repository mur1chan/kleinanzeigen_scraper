# Importieren der erforderlichen Bibliotheken
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import pandas as pd
import webbrowser

# Funktion, die Leerzeichen in einer Zeichenkette durch Bindestriche ersetzt
def check_string(product):
    return product.replace(' ', '-')

# Basisklasse für WebScraper
class WebScraper:
    def __init__(self):
        self.driver = None
        self.actions = None

    def start(self):
        # Initialisiert den Webdriver und die Aktionen
        self.driver = webdriver.Chrome()
        self.actions = ActionChains(self.driver)

    def load_url(self, url):
        # Lädt die angegebene URL im Browser
        if not self.driver:
            raise Exception("Browser not started")
        self.driver.get(url)
        self.driver.implicitly_wait(30)
        time.sleep(10)

    def find_element(self, xpath):
        # Findet ein Element im geladenen Webinhalt anhand seines XPath
        return self.driver.find_element(By.XPATH, xpath)

    def quit(self):
        # Schließt den Browser
        self.driver.close()

# WebScraper speziell für Produkte
class ProductScraper(WebScraper):
    # Funktion zum Ersetzen von "Heute" und "Gestern" durch das entsprechende Datum
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
        # Ruft die URL für das spezifische Produkt ab
        self.load_url(f"https://www.kleinanzeigen.de/s-{self.product}/k0")

    def get_product_url_pricerange(self, min_price, max_price):
        # Ruft die URL für das spezifische Produkt mit einem spezifischen Preisbereich ab
        self.load_url(f"https://www.kleinanzeigen.de/s-preis:{min_price}:{max_price}/{self.product}/k0")

    def accept_cookies(self):
        # Akzeptiert Cookies auf der Webseite
        cookies_accept = self.find_element('//*[@id="gdpr-banner-accept"]')
        self.actions.click(cookies_accept).perform()

    def get_elements_list_from_html(self):
        # Extrahiert die Produktinformationen aus dem HTML-Inhalt der Webseite
        elements_list = self.find_element("//*[@id='srchrslt-content']")
        items = elements_list.find_elements(By.XPATH, '//*[@id="srchrslt-adtable"]/li/article')
        self.get_items(items)

    def get_items(self, items):
        # Extrahiert die Einzelheiten jedes Produkts und speichert sie als JSON
        for item in items:
            # Hier werden die Produktdetails extrahiert
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

# Basisklasse für JSON
class DataWriter:
    def __init__(self, filename):
        self.filename = filename

    def write_data(self, data):
        raise NotImplementedError("Must be implemented by subclass")

# Eine Unterklasse von DataWriter
class JsonWriter(DataWriter):
    def write_data(self, new_data):
        # Schreibt Daten in eine JSON-Datei
        try:
            with open(self.filename, 'r+') as file:
                file_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            file_data = []

        file_data.append(new_data)

        with open(self.filename, 'w') as file:
            json.dump(file_data, file, indent=4)

# WebScraperApp ist die Hauptklasse, die die Benutzeroberfläche erstellt und alle Funktionen koordiniert
class WebScraperApp:
    def __init__(self, root):
        # Dies ist der Konstruktor der Klasse. Er initialisiert die Hauptelemente der GUI.
        # root: Tkinter-Root- oder Tkinter-Toplevel-Widget

        self.root = root
        self.root.title("Web Scraper")
        self.notebook = ttk.Notebook(root)  # Erstellt ein Notebook-Widget für die Tabs

        # Erstellt die Tabs
        self.create_scraper_tab()
        self.create_statistic_tab()

        self.notebook.pack(expand=True, fill='both')  # Packt das Notebook-Widget ins Fenster

    def clear_table(self):
        # Löscht alle Einträge in der Tabelle und in der zugehörigen JSON-Datei.
        # Wird aufgerufen, wenn der "Einträge löschen"-Knopf gedrückt wird.

        # Löscht alle Einträge in der Tabelle
        for item in self.product_table.get_children():
            self.product_table.delete(item)

        # Leert die JSON-Datei
        with open('data.json', 'w') as f:
            json.dump([], f)

    def create_scraper_tab(self):
        # Erstellt den "Scraper"-Tab.

        self.tab1 = ttk.Frame(self.notebook)  # Erstellt einen neuen Frame für den Tab
        self.notebook.add(self.tab1, text='Scraper')  # Fügt den Frame dem Notebook-Widget hinzu

        # Erstellt die Eingabefelder und Buttons
        self.product_entry = self.create_entry(self.tab1, "Produkt:", 0)
        self.min_price_entry = self.create_entry(self.tab1, "Min Preis:", 1)
        self.max_price_entry = self.create_entry(self.tab1, "Max Preis:", 2)

        # Erstellt den Start-Button und fügt ihn dem Tab hinzu
        self.start_button = tk.Button(self.tab1, text="Start", command=self.start_scraper_thread)
        self.start_button.grid(row=3, column=0, columnspan=2, pady=(0, 20))

        # Erstellt das Status-Label und fügt es dem Tab hinzu
        self.status_text = tk.StringVar()
        self.status_label = tk.Label(self.tab1, textvariable=self.status_text)
        self.status_label.grid(row=4, column=0, columnspan=2)

    def create_statistic_tab(self):
        # Erstellt den "Statistik"-Tab.

        self.tab2 = ttk.Frame(self.notebook)  # Erstellt einen neuen Frame für den Tab
        self.notebook.add(self.tab2, text='Statistik')  # Fügt den Frame dem Notebook-Widget hinzu

        # Erstellt den "Statistik berechnen"-Button und fügt ihn dem Tab hinzu
        self.calculate_button = tk.Button(self.tab2, text="Statistik berechnen", command=self.calculate_and_display_statistics)
        self.calculate_button.pack(pady=(20, 10))

        # Erstellt die Labels für die Statistiken und fügt sie dem Tab hinzu
        self.min_price_text = tk.StringVar()
        self.min_price_label = tk.Label(self.tab2, textvariable=self.min_price_text)
        self.min_price_label.pack()

        self.max_price_text = tk.StringVar()
        self.max_price_label = tk.Label(self.tab2, textvariable=self.max_price_text)
        self.max_price_label.pack()

        self.clear_button = tk.Button(self.tab2, text="Einträge löschen", command=self.clear_table)
        self.clear_button.pack(pady=(10, 0))

        self.median_price_text = tk.StringVar()
        self.median_price_label = tk.Label(self.tab2, textvariable=self.median_price_text)
        self.median_price_label.pack()

        # Erstellt die Tabelle und fügt sie dem Tab hinzu
        self.product_table = ttk.Treeview(self.tab2, columns=('title', 'price', 'location', 'upload', 'link'), show='headings')
        self.product_table.heading('title', text='Titel')
        self.product_table.heading('price', text='Preis')
        self.product_table.heading('location', text='Standort')
        self.product_table.heading('upload', text='Hochgeladen')
        self.product_table.heading('link', text='Link')
        self.product_table.pack(pady=(20, 0), fill='x')
        self.product_table.bind('<Double-1>', self.open_link)

    def create_entry(self, parent, label, row):
        # Hilfsmethode zum Erstellen von Eingabefeldern.

        # Erstellt ein Label und ein Eingabefeld und fügt sie dem parent-Widget hinzu.

        label = tk.Label(parent, text=label)
        label.grid(row=row, column=0, padx=(20, 10), pady=(20, 10))
        entry = tk.Entry(parent)
        entry.grid(row=row, column=1, padx=(0, 20), pady=(20, 10))
        return entry

    def run_scraper(self):
        # Führt den Scraper aus. Wird aufgerufen, wenn der "Start"-Knopf gedrückt wird.

        # Holt die Eingabewerte
        product = self.product_entry.get()
        min_price = self.min_price_entry.get()
        max_price = self.max_price_entry.get()

        # Überprüft die Eingabewerte und zeigt ggf. eine Fehlermeldung an
        if not product:
            messagebox.showerror("Fehler", "Bitte Produktname eingeben.")
            return
        if not min_price.isdigit() or not max_price.isdigit():
            messagebox.showerror("Fehler", "Preise müssen numerische Werte sein.")
            return

        # Startet den Scraper und zeigt den Status an
        self.status_text.set('Scraper gestartet ...')
        scraper = ProductScraper(product)
        scraper.start()
        scraper.get_product_url_pricerange(min_price, max_price)
        scraper.accept_cookies()
        scraper.get_elements_list_from_html()
        self.status_text.set('Scraper beendet.')

    def start_scraper_thread(self):
        # Startet den Scraper in einem neuen Thread. Dies verhindert, dass die GUI während des Scrapings einfriert.

        scraper_thread = threading.Thread(target=self.run_scraper)
        scraper_thread.start()

    def calculate_statistics(self, filename):
        # Berechnet die Statistiken auf Basis der gescrapten Daten.

        # filename: Der Name der JSON-Datei, die die gescrapten Daten enthält

        with open(filename, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)

        # Berechnet die Statistiken
        min_price = df['price'].min()
        min_product = df.loc[df['price'] == min_price].iloc[0].to_dict()
        max_price = df['price'].max()
        max_product = df.loc[df['price'] == max_price].iloc[0].to_dict()
        median_price = df['price'].median()

        return min_price, min_product, max_price, max_product, median_price

    def calculate_and_display_statistics(self):
        # Berechnet die Statistiken und zeigt sie an.

        min_price, min_product, max_price, max_product, median_price = self.calculate_statistics('data.json')

        # Zeigt die Statistiken an
        self.min_price_text.set(f'Min Preis: {min_price}, Produkt: {min_product}')
        self.max_price_text.set(f'Max Preis: {max_price}, Produkt: {max_product}')
        self.median_price_text.set(f'Median Preis: {median_price}')

        # Aktualisiert die Tabelle
        with open('data.json', 'r') as file:
            data = json.load(file)

        self.product_table.delete(*self.product_table.get_children())
        for item in data:
            self.product_table.insert('', 'end', values=(item['title'], item['price'], item['location'], item['upload'], item['link']))

    def open_link(self, event):
        # Öffnet den Link des ausgewählten Tabelleneintrags im Webbrowser.
        # Wird aufgerufen, wenn ein Tabelleneintrag doppelt angeklickt wird.

        item = self.product_table.focus()
        item_dict = self.product_table.item(item)
        webbrowser.open(item_dict['values'][-1])


if __name__ == "__main__":
    # Wenn das Skript direkt ausgeführt wird (anstatt als Modul importiert zu werden), wird die GUI erstellt und gestartet.
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()