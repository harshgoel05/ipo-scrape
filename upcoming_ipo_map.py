from datetime import datetime
import re
from time import sleep
from crawler_helper import scrape_page


UPCOMING_IPO = "https://ipowatch.in/upcoming-ipo-calendar-ipo-list/"
UPCOMING_SME_IPO = "https://ipowatch.in/upcoming-sme-ipo-calendar-list/"


def ipo_name_to_url_map(url):
    try:
        print(f"[DEBUG] {datetime.now()} -- Scraping {url} for IPO data")
        scraped_data = scrape_page(url)
        print(f"[DEBUG] {datetime.now()} -- Scraped {url} for IPO data")
        tables = scraped_data.find_all("table")  # Find all tables
        ipo_data = []  # Array to store the IPO name and URL objects

        if not tables:
            return ipo_data

        # Iterate through all tables
        for table in tables:
            rows = table.find_all("tr")[1:]  # Get all rows except the header row

            for row in rows:
                first_td = row.find("td")  # Get the first <td> element
                if first_td and first_td.find("a"):
                    ipo_name = first_td.get_text(strip=True).replace(
                        "\n", " "
                    )  # Extract the IPO name (text in <td>) and replace newlines with space
                    ipo_url = first_td.find("a")[
                        "href"
                    ]  # Extract the URL from the <a> tag
                    ipo_data.append(
                        {"name": ipo_name, "url": ipo_url}
                    )  # Append as object

        print(f"[DEBUG] {datetime.now()} -- Returning IPO data for url {url}")
        return ipo_data
    except Exception as e:
        print(f"Error getting {url} IPO data: {e}")
        return None


def get_gmp_url_for_stocks():
    print(
        f"[DEBUG] {datetime.now()} -- Getting Mainboard GMP URLs for stocks, after sleep 5"
    )
    sleep(1)
    upcoming = ipo_name_to_url_map(UPCOMING_IPO)
    print(
        f"[DEBUG] {datetime.now()} -- Getting SME GMP URLs for SME stocks, after sleep 5"
    )
    sleep(1)
    sme = ipo_name_to_url_map(UPCOMING_SME_IPO)
    print(f"[DEBUG] {datetime.now()} -- Returning Mainboard and SME GMP URLs")
    return upcoming + sme


def get_urls_by_names(name, data_list):
    # Normalize the input name (remove common words like Ltd, Pvt, etc., and lowercase it)
    cleaned_name = (
        re.sub(
            r"\b(ltd|pvt|industries|solutions|international|technologies)\b",
            "",
            name,
            flags=re.IGNORECASE,
        )
        .strip()
        .lower()
    )

    for data in data_list:
        if cleaned_name in data["name"].lower() or data["name"].lower() in cleaned_name:
            url = data["url"]
            cleaned_url = (
                re.sub(
                    r"\b(-ltd|-pvt|-industries|-solutions|-international|-technologies|-india)\b",
                    "",
                    url,
                    flags=re.IGNORECASE,
                )
                .strip()
                .lower()
            )
            # Replace specific part of the URL if needed
            cleaned_url = cleaned_url.replace(
                "ipo-date-review-price-allotment-details", "ipo-gmp-grey-market-premium"
            )
            return cleaned_url

    return None
