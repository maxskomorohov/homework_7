import csv
from bs4 import BeautifulSoup
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

class Scraper:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def scrap_page(self, url, timeout=(5, 10)):
        self.driver.get(url)
        time.sleep(random.randint(*timeout))
        return self.driver.page_source

    def get_pagination_count(self, page_source):
        try:
            # Find link to the last pagination page
            last_a = self.driver.find_element(By.CSS_SELECTOR, "div.paginator div.list a:last-of-type")
            # Get link's numeric value (equals pagination pages total)
            return int(last_a.text.strip())
        except (NoSuchElementException, ValueError):
            print(f'Пагінації для цього товара немає')
            return None

    def parse_iphones(self, page_source):
        soup = BeautifulSoup(page_source, "lxml")

        found_items = []

        items_list = soup.select('rz-category-goods div.item')
        for item in items_list:
            def clean_price(text):
                if not text:
                    return None
                cleaned = text.replace('\xa0', '').replace('\n', '').replace('₴', '')
                return re.sub(r'\s+', '', cleaned)

            # Product title
            title_tag = item.select_one('a.tile-title')
            title = title_tag.text.strip() if title_tag else ""

            # Product status (available, ending, etc.)
            status_tag = item.select_one('rz-tile-sell-status')
            status = status_tag.text.strip() if status_tag else ""

            # Product current price
            current_price_tag = item.select_one('div.price')
            current_price = clean_price(current_price_tag.text) if current_price_tag else ""

            # Product old price
            old_price_tag = item.select_one('div.old-price')
            old_price = clean_price(old_price_tag.text) if old_price_tag else ""

            # Product URL
            url_tag = item.select_one('a.tile-image-host')
            url = url_tag['href'] if url_tag and url_tag.has_attr('href') else ""

            # Skipping empty marketing cards in products list
            if not any([title, status, current_price, old_price, url]):
                continue

            # Skipping broken cards (with no values) if any
            found_items.append([title, status, current_price, old_price, url])

        return found_items

    def save_items_to_file(self, items, filename):
        with open(filename, 'w', newline='', encoding='utf8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Назва товару', 'Статус', 'Поточна ціна', 'Стара ціна', 'Посилання'])
            for item in items:
                writer.writerow(item)