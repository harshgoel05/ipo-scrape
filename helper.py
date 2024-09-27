import re
from datetime import datetime


def parse_lot_size(input_string):
    try:
        pattern = r"Lot size\s*(\d+)(?:\s*—\s*₹(\d+))?"
        match = re.search(pattern, input_string)
        if match:
            lot_size = int(match.group(1))
            min_investment = int(match.group(2)) if match.group(2) else 0
            return lot_size, min_investment
        else:
            raise ValueError("Input string does not match the expected format.")
    except ValueError as e:
        print(f"Error parsing lot size: {e}")
        return None, None
    
def convert_to_iso_format(date_str):
    # Try different patterns for parsing
    try:
        # Case with time provided, e.g., "27 Sep 2024 (5 PM)"
        if '(' in date_str:
            date_part, time_part = date_str.split('(')
            date_part = date_part.strip()
            time_part = time_part.replace(')', '').strip()
            # Parse time with AM/PM
            time = datetime.strptime(time_part, '%I %p').time()
        else:
            # Default time if not provided
            date_part = date_str.strip()
            time = datetime.min.time()  # Default to 12:00 AM

        # Parse the date part, e.g., "25 Sep 2024"
        date = datetime.strptime(date_part, '%d %b %Y')

        # Combine date and time
        combined = datetime.combine(date, time)
        
        # Convert to ISO 8601 format
        return combined.isoformat()

    except ValueError as e:
        return f"Error: {e}"
    
def process_listing_date(listing_date_str):
    try:
        if(listing_date_str.strip() == '–'):
            return None
        # Parse the listing date
        listing_date = datetime.strptime(listing_date_str.strip(), "%d %b %Y")
        
        # Add the specific time (9am IST)
        listing_date = listing_date.replace(hour=9, minute=0)
        
        # Format the date with time
        return listing_date.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        print(f"Error parsing listing date: {listing_date_str}")  # Debug print
        return None
    
def process_price_range(price_range):
    if(price_range == '-'):
        return None
    # Remove the Rupee symbol and split the range
    prices = re.sub(r'[^\d\s–]', '', price_range).split('–')
    
    try:
        min_price = int(prices[0].strip())
        max_price = int(prices[-1].strip()) if len(prices) > 1 else min_price
        return min_price, max_price
    except ValueError:
        return None, None


def process_ipo_date(ipo_date):
    # Split the date range
    dates = ipo_date.split('–')
    
    def parse_date(date_str, reference_date=None):
        # Remove ordinal suffixes and extra spaces
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str.strip())
        
        if(date_str == 'To be announced'):
            return None

        # Split the date string into components
        parts = date_str.split()
        
        # If only day is provided, add month and year from reference date
        if len(parts) == 1 and reference_date:
            parts.append(reference_date.strftime("%b"))
            parts.append(str(reference_date.year))
        elif len(parts) == 2 and reference_date:
            parts.append(str(reference_date.year))
        
        # Combine parts back into a string
        date_str = " ".join(parts)
        
        try:
            parsed_date = datetime.strptime(date_str, "%d %b %Y")
            
            # Adjust year if necessary (for start date)
            if reference_date and parsed_date > reference_date:
                if parsed_date.month == 12 and reference_date.month == 1:
                    parsed_date = parsed_date.replace(year=reference_date.year - 1)
                elif parsed_date.month == 1 and reference_date.month == 12:
                    parsed_date = parsed_date.replace(year=reference_date.year + 1)
            
            return parsed_date
        except ValueError:
            print(f"Error parsing date: {date_str}")  # Debug print
            return None

    # Parse end date first (it's usually more complete)
    end_date = parse_date(dates[-1] if len(dates) > 1 else dates[0])
    
    # Parse start date using end date as reference
    start_date = parse_date(dates[0], reference_date=end_date)
    
    # Add specific times
    if start_date:
        start_date = start_date.replace(hour=10, minute=0)  # 10am IST
    if end_date:
        end_date = end_date.replace(hour=17, minute=0)  # 5pm IST
    
    # Format dates with times
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S") if start_date else None
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S") if end_date else None
    
    return start_date_str, end_date_str


def write_json(json_data,file_name):
    try:
        with open(file_name, 'w') as f:
            f.write(json_data)
    except Exception as e:
        print(f"Error writing to file: {e}")


def parse_symbol(text):
    # Use regex to find all words that are in uppercase and return them as a list
    symbols = re.findall(r'\b[A-Z]+\b', text)
    # Filter out any words that are not entirely uppercase
    return symbols[0]


def find(arr , id):
    for x in arr:
        if x["symbol"] == id:
            return [x]



def convert_to_slug(company_name):
    # Step 1: Convert to lowercase
    company_name = company_name.lower()

    # Step 2: Replace spaces and special characters with hyphens
    company_name = company_name.replace(' ', '-')

    # Step 3: Add "-ttd" suffix to the company name
    slug = f"{company_name}-ttd"

    return slug
