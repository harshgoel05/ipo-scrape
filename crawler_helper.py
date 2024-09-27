from datetime import datetime
from constants import CRAWL_BASE_URL, CRAWL_HOME_PAGE

import requests
from bs4 import BeautifulSoup


def crawl_home_page():
    try:
        r = requests.get(CRAWL_BASE_URL  + CRAWL_HOME_PAGE)
        soup = BeautifulSoup(r.content, 'html.parser')
        tables = soup.find('div', id="ipos").findAll('table')
        rows = []
        rows.extend(tables[0].find('tbody').find_all('tr'))
        rows.extend(tables[1].find('tbody').find_all('tr'))
        return rows
    except Exception as e:
        print(f"[DEBUG] {datetime.now()} Error crawling home page: {e}")
        return None


def scrape_page(link):
    try:
        r = requests.get(link)
        soup = BeautifulSoup(r.content, 'html.parser')
        # Return Div instead of soup
        return soup
    except Exception as e:
        print(f"[DEBUG] {datetime.now()} Error crawling stock page link - {link} Error - {e}")
        return None