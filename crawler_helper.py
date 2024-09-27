from constants import CRAWL_BASE_URL, CRAWL_HOME_PAGE

import requests
from bs4 import BeautifulSoup


def crawl_home_page():
    try:
        r = requests.get(CRAWL_BASE_URL  + CRAWL_HOME_PAGE)
        soup = BeautifulSoup(r.content, 'html.parser')
        rows = soup.find('div', id="ipos").find('table').find('tbody').find_all('tr')
        return rows
    except Exception as e:
        print(f"Error crawling home page: {e}")
        return None


def crawl_stock_page(link):
    try:
        r = requests.get(link)
        soup = BeautifulSoup(r.content, 'html.parser')
        # Return Div instead of soup
        return soup
    except Exception as e:
        print(f"Error crawling stock page: {e}")
        return None