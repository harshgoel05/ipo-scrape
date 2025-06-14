import re
from datetime import datetime, timedelta, timezone


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
        print(f"[DEBUG] {datetime.now()} Error parsing lot size: {input_string} {e}")
        return None, None


def parse_schedule_date(date_str):
    # Try different patterns for parsing
    try:
        # Case with time provided, e.g., "27 Sep 2024 (5 PM)"
        if "(" in date_str:
            date_part, time_part = date_str.split("(")
            date_part = date_part.strip()
            time_part = time_part.replace(")", "").strip()
            # Parse time with AM/PM
            time = datetime.strptime(time_part, "%I %p").time()
        else:
            # Default time if not provided
            date_part = date_str.strip()
            time = datetime.min.time()  # Default to 12:00 AM

        # Parse the date part, e.g., "25 Sep 2024"
        date = datetime.strptime(date_part, "%d %b %Y")

        # Combine date and time
        combined = datetime.combine(date, time)

        ist_timezone = timezone(timedelta(hours=5, minutes=30))
        combined = combined.replace(tzinfo=ist_timezone)

        # Format the date with time and timezone offset
        return (
            combined.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]
            + ":"
            + combined.strftime("%z")[-2:]
        )

    except Exception as e:
        print(
            f"[DEBUG] {datetime.now()} Error converting to ISO format: {date_str} {e}"
        )
        return None


def process_listing_date(listing_date_str):
    try:
        if listing_date_str.strip() == "-" or listing_date_str.strip() == "\u2013":
            return None

        # Parse the listing date
        listing_date = datetime.strptime(listing_date_str.strip(), "%d %b %Y")

        # Add the specific time (9 AM IST)
        listing_date = listing_date.replace(hour=9, minute=0)

        # Make the datetime timezone-aware (IST is UTC+5:30)
        ist_timezone = timezone(timedelta(hours=5, minutes=30))
        listing_date = listing_date.replace(tzinfo=ist_timezone)

        # Format the date with time and timezone offset
        return (
            listing_date.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]
            + ":"
            + listing_date.strftime("%z")[-2:]
        )

    except Exception as e:
        print(
            f"[DEBUG] {datetime.now()} Error parsing listing date: {listing_date_str}",
            e,
        )
        return None


def process_price_range(price_range):
    try:
        # Check if the input is a dash or en-dash, indicating no range
        if price_range in ["-", "\u2013"]:
            return None, None

        # Extract prices using regex to handle various formats and remove non-digit characters
        matches = re.findall(r"₹\s*(\d+)", price_range)

        # If no valid price matches are found
        if not matches:
            return None, None

        # Convert matched prices to integers
        prices = list(map(int, matches))

        # Get min and max prices; if only one price, both min and max are the same
        min_price = prices[0]
        max_price = prices[1] if len(prices) > 1 else min_price

        return min_price, max_price

    except ValueError:
        print(f"[DEBUG] {datetime.now()} Error parsing price range: {price_range}")
        return None, None


def process_ipo_date(ipo_date):
    # Split the date range
    dates = ipo_date.split("–")

    def parse_date(date_str, reference_date=None):
        # Remove ordinal suffixes and extra spaces
        date_str = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str.strip())

        if date_str == "To be announced":
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
            print(f"[DEBUG] {datetime.now()} Error parsing ipo date: {date_str}")
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
    start_date = (
        start_date.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))
        if start_date
        else None
    )
    end_date = (
        end_date.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))
        if end_date
        else None
    )

    # Format with timezone information
    start_date_str = (
        start_date.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]
        + ":"
        + start_date.strftime("%z")[-2:]
        if start_date
        else None
    )
    end_date_str = (
        end_date.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]
        + ":"
        + end_date.strftime("%z")[-2:]
        if end_date
        else None
    )

    return start_date_str, end_date_str


def write_json(json_data, file_name):
    try:
        with open(file_name, "w") as f:
            f.write(json_data)
    except Exception as e:
        print(f"Error writing to file: {e}")


def parse_symbol(text):
    # Use regex to find all words that are in uppercase and return them as a list
    symbols = re.findall(r"\b[A-Z]+\b", text)
    # Return the first symbol if any are found
    return symbols[0] if symbols else None


def find(arr, id):
    for x in arr:
        if x["symbol"] == id:
            return [x]


def extract_symbols(arr):
    slugs = []
    for x in arr:
        slugs.append(x["symbol"])
    return slugs


def extract_names(arr):
    slugs = []
    for x in arr:
        slugs.append(x["name"])
    return slugs


def convert_to_slug(company_name):
    # Step 1: Convert to lowercase
    company_name = company_name.lower()

    # Step 2: Replace spaces and special characters with hyphens
    company_name = company_name.replace(" ", "-")

    # Step 3: Add "-ttd" suffix to the company name
    slug = f"{company_name}"
    # Remove ltd from the slug if present at the end
    if slug.endswith("-ltd"):
        slug = slug.replace("-ltd", "")
    return slug


def convert_gmp_date(date_str):
    # Get current date and year
    today = datetime.today()
    current_year = today.year

    # If the date string is 'Today', return today's date in the desired format
    if date_str.lower() == "today":
        ist_timezone = timezone(timedelta(hours=5, minutes=30))
        today = today.replace(tzinfo=ist_timezone)
        return (
            today.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2] + ":" + today.strftime("%z")[-2:]
        )

    # Try to parse the date string into a datetime object
    try:
        # Special handling for dates that include only day and month
        date_obj = datetime.strptime(date_str, "%d %B")

        # Initially assume the date is in the current year
        date_obj = date_obj.replace(year=current_year)

        # Handle year transitions
        if today.month == 1 and date_obj.month == 12:
            # If it's January now but the date is December, assign the previous year
            date_obj = date_obj.replace(year=current_year - 1)
        elif today.month == 12 and date_obj < today:
            # If it's December and the date has already passed, assign the next year
            date_obj = date_obj.replace(year=current_year + 1)

    except ValueError:
        # Return None if parsing fails
        return None

    # Convert to IST timezone
    ist_timezone = timezone(timedelta(hours=5, minutes=30))
    date_obj = date_obj.replace(tzinfo=ist_timezone)

    # Return the date in the desired ISO format with timezone
    return (
        date_obj.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]
        + ":"
        + date_obj.strftime("%z")[-2:]
    )
