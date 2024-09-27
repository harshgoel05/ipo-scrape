import json
from crawler_helper import crawl_home_page
from helper import find, write_json
from parse_home_page import parse_home_page
from process_individual_stock import process_individual_stock

def process_stocks_info(stock_data):
    updated_stock_data = []
    for stock in stock_data:
        try:
            print(f"Symbol: {stock['symbol']}")
            # Find the individual stock data in stock_data using symbol and add to json in stock_details
            stock['details'] = process_individual_stock(stock)
            updated_stock_data.append(stock)
        except Exception as e:
            print(f"Error processing stock: {stock['symbol']}")
            print(e)
    return updated_stock_data


# Main function
if __name__ == '__main__':

    home_page_rows = crawl_home_page()
    stock_data = parse_home_page(home_page_rows)

    # individual_stock_data = process_stocks_info(stock_data)

    individual_stock_data = process_stocks_info(find(stock_data, "HYUNDAI"))
    
    individual_stock_data_json_data = json.dumps(individual_stock_data, indent=2)

    write_json(individual_stock_data_json_data, 'stock_data_individual.json')

    print("Data written to stock_data_individual.json")


