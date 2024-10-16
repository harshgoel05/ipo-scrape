from crawler_helper import scrape_page
from datetime import datetime
from helper import convert_gmp_date

# ------------------------------------------------
# Function to get GMP timeline for a stock
# @param gmp_url - URL of the GMP page
# @return stock_data - List of GMP data
# ------------------------------------------------
def get_gmp_timeline(gmp_url):
    try:
        if not gmp_url:
            print(f"[DEBUG] {datetime.now()} No GMP URL found")
            return None
        else:
            return parse_gmp_page(gmp_url)
    except Exception as e:
        print(f"[DEBUG] {datetime.now()} Error parsing GMP timeline for {gmp_url}")
        print(e)
        return None

#  ------------------------------------------------
#  Function to parse GMP page
#  @param gmp_url - URL of the GMP page
#  @return stock_data - List of GMP data
#  ------------------------------------------------
def parse_gmp_page(gmp_url):
    data = scrape_page(gmp_url)
    if not data:
        print(f"[DEBUG] {datetime.now()} No Data Error scraping gmp page: {gmp_url}")
        return None
    is_error = data.find('h1', class_='elementor-heading-title').text.strip()
    if is_error == '404':
        print(f"[DEBUG] {datetime.now()} 404 Error scraping gmp page: {gmp_url}")
        return None

    table_cont = data.find('figure', class_='wp-block-table')
    table = table_cont.find('tbody')
    if not table:
        print(f"[DEBUG] {datetime.now()} No table found Error scraping gmp page: {gmp_url}")
        return None
    
    # Initialize an empty list to store the data
    stock_data = []
    
    # Iterate over table rows, skipping the header
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        
        date = cols[0].get_text().strip()  # Extract and clean the date
        gmp = cols[1].get_text().strip()   # Extract the GMP value
        
        # Remove ₹ symbol and handle '-' as null
        gmp_cleaned = None if gmp in ['₹-', '-', '\u2013'] else int(gmp.replace('₹', '').replace(',', '').strip())

        # Append the data to the list in the required format
        stock_data.append({
            'date': convert_gmp_date(date),
            'price': gmp_cleaned
        })
    
    return stock_data
