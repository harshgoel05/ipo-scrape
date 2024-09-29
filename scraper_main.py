
from datetime import datetime
import json
from time import sleep
from constants import CRAWL_BASE_URL, CRAWL_HOME_PAGE
from crawler_helper import scrape_page
from helper import extract_names, write_json
from parse_gmp import get_gmp_timeline
from parse_home_page import parse_home_page
from process_individual_stock import get_full_ipo_details
from upcoming_ipo_map import get_gmp_url_for_stocks, get_urls_by_names

# ------------------------------------------------
#  Function to get all IPO listing with GMP link
# @return all_stocks_with_gmp_url - List of all IPOs with GMP URL
# ------------------------------------------------

def get_all_ipo_listing_with_gmp_link():
    # Fetch the table which has all the stock data
    home_page_html = scrape_page(CRAWL_BASE_URL  + CRAWL_HOME_PAGE)
    # Parse the table to get all the stock data
    all_stocks_from_table = parse_home_page(home_page_html)

    print(f"Total stocks found: {len(all_stocks_from_table)}")
    print("Stocks found:", extract_names(all_stocks_from_table))


    # Fetch GMP URLs available from ipowatch.in
    gmp_urls = get_gmp_url_for_stocks()
    print(f"Total GMP URLs found: {len(gmp_urls)}")

    all_stocks_with_gmp_url = []
    for stock in all_stocks_from_table:
        stock['gmpUrl'] = get_urls_by_names(stock['name'], gmp_urls)
        all_stocks_with_gmp_url.append(stock)
    # Return the list of all stocks with GMP URL
    return all_stocks_with_gmp_url
 

# ------------------------------------------------
#  Function to get stock details and GMP from symbol
# @param symbol - Stock symbol
# @param gmp_url - GMP URL
# @return stock - Stock details and GMP
# ------------------------------------------------

def get_stock_details_and_gmp_from_symbol(details_url,gmp_url):
    stock = {}
    print(f"[DEBUG] {datetime.now()} Fetching full ipo details for: {details_url} after sleep 5")
    sleep(1)
    if details_url:
        stock['details'] = get_full_ipo_details(details_url)
    print(f"[DEBUG] {datetime.now()} Fetching GMP timeline for: {gmp_url} after sleep 5")
    sleep(1)
    if gmp_url:
        stock['gmpTimeline'] = get_gmp_timeline(gmp_url)
    return stock

 
# ------------------------------------------------
# Function to get details and GMP for all IPO
# @param stock_data - List of all IPOs
# @return updated_stock_data - List of all IPOs with details and GMP
# ------------------------------------------------
def get_details_and_gmp_for_all_ipo(stock_data):
    updated_stock_data = []
    for stock in stock_data:
        stock_details = get_stock_details_and_gmp_from_symbol(stock['symbol'], stock['gmpUrl'])
        updated_stock_data["detials"] = stock_details["details"]
        updated_stock_data["gmpTimeline"] = stock_details["gmpTimeline"]
        updated_stock_data.append(stock)
    return updated_stock_data


# Main function
if __name__ == '__main__':

    all_stocks_with_gmp = get_all_ipo_listing_with_gmp_link()

    # Fetch all the individual stock data
    individual_stock_data = get_details_and_gmp_for_all_ipo(all_stocks_with_gmp)
    individual_stock_data_json_data =  json.dumps(individual_stock_data, indent=2)

    write_json(individual_stock_data_json_data, 'stocks.json')

    print("Data written to stocks.json")




