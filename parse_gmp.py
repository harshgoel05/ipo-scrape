from crawler_helper import scrape_page

from datetime import datetime, timedelta

def convert_date(date_str):
    # Get current date and year
    today = datetime.today()
    current_year = today.year

    # If the date string is 'Today', return today's date in the desired format
    if date_str.lower() == 'today':
        return today.strftime('%Y-%m-%dT00:00:00')

    # Try to parse the date string into a datetime object
    try:
        # Special handling for dates that include only day and month
        date_obj = datetime.strptime(date_str, '%d %B')
        date_obj = date_obj.replace(year=current_year)

        # Handle dates in the next year if today is late in the year and the given date has passed
        if date_obj < today and today.month == 12:
            date_obj = date_obj.replace(year=current_year + 1)

    except ValueError:
        return None

    # Return the date in the desired format
    return date_obj.strftime('%Y-%m-%dT00:00:00')


    
def get_gmp_timeline(stock):
    try:
        return get_gmp_timeline_from_stock_name(stock)
    except Exception as e:
        print(f"[DEBUG] {datetime.now()} Error getting GMP timeline for {stock['symbol']}")
        print(e)
        return None


def get_gmp_timeline_from_stock_name(stock):
    if not stock.get('gmpUrl'):
        print(f"[DEBUG] {datetime.now()} No GMP URL found for {stock['symbol']}")
        return None
    data = scrape_page(stock.get('gmpUrl'))
    if not data:
        print(f"[DEBUG] {datetime.now()} No Data Error scraping gmp page: {stock['symbol']}")
        return None
    is_error = data.find('h1', class_='elementor-heading-title').text.strip()
    if is_error == '404':
        print(f"[DEBUG] {datetime.now()} 404 Error scraping gmp page: {stock['symbol']}")
        return None

    table_cont = data.find('figure', class_='wp-block-table')
    table = table_cont.find('tbody')
    if not table:
        print(f"[DEBUG] {datetime.now()} No table found Error scraping gmp page: {stock['symbol']}")
        return None
    
    # Initialize an empty list to store the data
    stock_data = []
    
    # Iterate over table rows, skipping the header
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        
        date = cols[0].get_text().strip()  # Extract and clean the date
        gmp = cols[1].get_text().strip()   # Extract the GMP value
        
        # Remove ₹ symbol and handle '-' as null
        gmp_cleaned = None if gmp == '₹-' or gmp == '-' or gmp == '\u2013' else int(gmp.replace('₹', '').strip())
        
        # Append the data to the list in the required format
        stock_data.append({
            'date': convert_date(date),
            'price': gmp_cleaned
        })
    
    return stock_data
