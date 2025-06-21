from constants import CRAWL_BASE_URL
from helper import (
    convert_to_slug,
    parse_symbol,
    process_ipo_date,
    process_listing_date,
    process_price_range,
)


def collect_all_ipo_rows(html_content):
    """
    Collect all IPO rows from both desktop and mobile views.

    Args:
        html_content: BeautifulSoup object of the HTML content

    Returns:
        list: List containing all row elements found
    """
    all_rows = []

    # First collect desktop view rows
    table_containers = html_content.find_all("div", class_="table-container")
    for container in table_containers:
        tables = container.find_all("table")
        for table in tables:
            tbody = table.find("tbody")
            if tbody:
                rows = tbody.find_all("tr")
                all_rows.extend(rows)

    # Then collect mobile view cards
    mobile_container = html_content.find("div", class_="show-on-mobile")
    if mobile_container:
        cards = mobile_container.find_all("div", class_="card")
        all_rows.extend(cards)

    return all_rows


def parse_home_page(home_page_html):
    try:
        stock_data = []
        for row in collect_all_ipo_rows(home_page_html):
            # Extract the required information
            logo_url = row.find("img")["src"]
            symbol_str = row.find("span", class_="ipo-symbol").text.strip()
            symbol = parse_symbol(symbol_str)
            link = row.find("td", class_="name").find("a").get("href")
            name = row.find("span", class_="ipo-name").text.strip()
            ipo_date = row.find("td", class_="date").text.split("\n")[2].strip()
            listing_date = row.find_all("td", class_="date")[1].text.strip()
            price_range = row.find("td", class_="text-right").text.strip()

            # Process IPO date
            ipo_start_date, ipo_end_date = process_ipo_date(ipo_date)

            # Process price range
            min_price, max_price = process_price_range(price_range)
            processed_listing_date = process_listing_date(listing_date)
            # Create a dictionary for the current stock
            stock_info = {
                "logoUrl": logo_url,
                "link": CRAWL_BASE_URL + link,
                "symbol": symbol,
                "name": name,
                "startDate": ipo_start_date,
                "endDate": ipo_end_date,
                "listingDate": processed_listing_date,
                "priceRange": {"min": min_price, "max": max_price},
                "slug": convert_to_slug(name),
            }

            # Append the stock info to the list
            stock_data.append(stock_info)
        return stock_data
    except Exception as e:
        print(f"Error parsing home page: {e}")
        return None
