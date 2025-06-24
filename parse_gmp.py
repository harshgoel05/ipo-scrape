from crawler_helper import scrape_page
from datetime import datetime
from helper import convert_gmp_date
import re


# ------------------------------------------------
# Function to get GMP timeline for a stock
# @param gmp_url - URL of the GMP page
# @return stock_data - GMP data object
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


def _parse_gmp_timeline(data):
    try:
        table_cont = data.find("figure", class_="wp-block-table")
        table = table_cont.find("tbody") if table_cont else None
        if not table:
            print(f"[DEBUG] {datetime.now()} No GMP timeline table found")
            return []

        gmp_timeline = []
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")

            date = cols[0].get_text().strip()
            gmp = cols[1].get_text().strip()

            gmp_cleaned = (
                None
                if gmp in ["₹-", "-", "–"]
                else int(gmp.replace("₹", "").replace(",", "").strip())
            )

            gmp_timeline.append({"date": convert_gmp_date(date), "price": gmp_cleaned})
        return gmp_timeline
    except Exception as e:
        print(f"[DEBUG] {datetime.now()} Error parsing GMP timeline: {e}")
        return []


def _parse_ipo_details(data):
    try:
        all_tables = data.find_all("figure", class_="wp-block-table")

        table_cont = None
        if len(all_tables) > 1:
            table_cont = all_tables[1]
        else:
            print(f"[DEBUG] {datetime.now()} Not enough tables for IPO details")
            return None

        table = table_cont.find("tbody") if table_cont else None
        if not table:
            print(f"[DEBUG] {datetime.now()} No tbody in IPO details table.")
            return None

        details = {}
        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 2:
                key = (
                    re.sub(r"\s+", " ", cols[0].get_text(strip=True))
                    .replace(":", "")
                    .strip()
                )
                value_cell = cols[1]
                value_text = re.sub(
                    r"\s+", " ", value_cell.get_text(strip=True)
                ).strip()
                if key == "Offer for Sale":
                    text = value_text.replace(",", "")
                    numbers = re.findall(r"\d+", text)
                    if numbers:
                        details["offerForSale"] = int("".join(numbers))
                elif key == "IPO Listing":
                    details["ipoListing"] = value_text
                elif key == "Face Value":
                    text = value_text
                    numbers = re.findall(r"(\d+)", text)
                    if numbers:
                        details["faceValue"] = int(numbers[0])
                elif key == "Retail Quota":
                    text = value_text
                    numbers = re.findall(r"\d+", text)
                    if numbers:
                        details["retailQuota"] = int(numbers[0])
                elif key == "QIB Quota":
                    text = value_text
                    numbers = re.findall(r"\d+", text)
                    if numbers:
                        details["qibQuota"] = int(numbers[0])
                elif key == "NII Quota":
                    text = value_text
                    numbers = re.findall(r"\d+", text)
                    if numbers:
                        details["niiQuota"] = int(numbers[0])
                elif key == "DRHP Draft Prospectus":
                    link = value_cell.find("a")
                    details["drhpLink"] = (
                        link["href"]
                        if link and link.has_attr("href") and link["href"] != "#"
                        else None
                    )
                elif key == "RHP Draft Prospectus":
                    link = value_cell.find("a")
                    details["rhpLink"] = (
                        link["href"]
                        if link and link.has_attr("href") and link["href"] != "#"
                        else None
                    )
                elif key == "Anchor Investors List":
                    link = value_cell.find("a")
                    details["anchorInvestorsLink"] = (
                        link["href"]
                        if link and link.has_attr("href") and link["href"] != "#"
                        else None
                    )
        return details
    except Exception as e:
        print(f"[DEBUG] {datetime.now()} Error parsing IPO details from GMP page: {e}")
        return None


#  ------------------------------------------------
#  Function to parse GMP page
#  @param gmp_url - URL of the GMP page
#  @return stock_data - GMP data object
#  ------------------------------------------------
def parse_gmp_page(gmp_url):
    data = scrape_page(gmp_url)
    if not data:
        print(f"[DEBUG] {datetime.now()} No Data Error scraping gmp page: {gmp_url}")
        return None
    is_error = data.find("h1", class_="elementor-heading-title").text.strip()
    if is_error == "404":
        print(f"[DEBUG] {datetime.now()} 404 Error scraping gmp page: {gmp_url}")
        return None

    gmp_data = {}
    gmp_data["gmpTimeline"] = _parse_gmp_timeline(data)
    gmp_data["ipoDetails"] = _parse_ipo_details(data)

    return gmp_data
