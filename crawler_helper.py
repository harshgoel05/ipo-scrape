from datetime import datetime
from constants import CRAWL_BASE_URL, CRAWL_HOME_PAGE

import requests
from bs4 import BeautifulSoup


# ------------------------------------------------
#  Function to scrape a page
#  @param link - URL of the page to scrape
#  @return soup - BeautifulSoup object
# ------------------------------------------------
# 
def scrape_page(link):
    try:
        r = requests.get(link)
        soup = BeautifulSoup(r.content, 'html.parser')
        return soup
    except Exception as e:
        print(f"[ERROR] {datetime.now()} Error crawling stock page link - {link} Error - {e}")
        return None