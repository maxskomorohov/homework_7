from scraper import Scraper
from pprint import pprint

BASE_URL = "https://rozetka.com.ua/ua/"
MODIFIER_MOB = "mobile-phones/c80003/"
PARAM_PRODUCER = "producer=apple/"

url_iphones = BASE_URL + MODIFIER_MOB + PARAM_PRODUCER

with Scraper() as scraper:
    page_source = scraper.scrap_page(url_iphones, (10, 20))
    pagination_count = scraper.get_pagination_count(page_source)
    print(pagination_count)

    parsed_items = scraper.parse_iphones(page_source)
    pprint(parsed_items)

    if pagination_count:
        for i in range(2, pagination_count + 1):
            url_iphones_paginated = f"{BASE_URL}{MODIFIER_MOB}page={i};{PARAM_PRODUCER}"
            page_source = scraper.scrap_page(url_iphones_paginated, (10, 20))

            paginated_items = scraper.parse_iphones(page_source)
            parsed_items.extend(paginated_items)

    pprint(parsed_items)

    scraper.save_items_to_file(parsed_items, 'iphones.csv')