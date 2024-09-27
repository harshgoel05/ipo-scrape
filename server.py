import json
from time import sleep
from crawler_helper import crawl_home_page
from helper import find, extract_symbols, write_json
from parse_gmp import get_gmp_timeline
from parse_home_page import parse_home_page
from process_individual_stock import get_full_ipo_details

def process_stocks_info(stock_data):
    updated_stock_data = []
    for stock in stock_data:
        try:
            print(f"Fetching Symbol: {stock['name']}")
            # Find the individual stock data in stock_data using symbol and add to json in stock_details
            sleep(5)
            stock['details'] = get_full_ipo_details(stock)
            sleep(5)
            stock['gmpTimeline'] = get_gmp_timeline(stock)
            updated_stock_data.append(stock)
        except Exception as e:
            print(f"Error fetching stock: {stock['symbol']}")
            print(e)
    return updated_stock_data


# Main function
if __name__ == '__main__':

    # Fetch the table which has all the stock data
    home_page_rows = crawl_home_page()
    all_stocks_from_table = parse_home_page(home_page_rows)

    print(f"Total stocks found: {len(all_stocks_from_table)}")
    print("Stocks found:", extract_symbols(all_stocks_from_table))

    # Fetch all the individual stock data
    individual_stock_data = process_stocks_info(all_stocks_from_table)
    individual_stock_data_json_data = json.dumps(individual_stock_data, indent=2)

    write_json(individual_stock_data_json_data, 'stocks.json')

    print("Data written to stocks.json")


