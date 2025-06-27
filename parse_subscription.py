from datetime import datetime


def parse_subscription_page(soup):
    ipo_blocks = soup.find_all("div", class_="watermark")
    ipos = []
    for block in ipo_blocks:
        try:
            ipo = parse_ipo_block(block)
            ipos.append(ipo)
        except Exception as e:
            print(f"[ERROR] Error parsing IPO block: {e}")
            continue
    return ipos


def parse_ipo_block(block):
    def clean(text):
        return text.strip().replace("\xa0", " ").replace("\n", " ").strip()

    ipo = {}
    main_table = block.find("table")
    rows = main_table.find_all("tr")

    # IPO name and type
    name_type = clean(rows[0].text)
    if "(" in name_type and ")" in name_type:
        ipo["name"] = name_type.split("(")[0].strip()
        ipo["type"] = name_type.split("(")[-1].replace(")", "").strip()
    else:
        ipo["name"] = name_type
        ipo["type"] = None

    # Date range and price band
    date_price_row = rows[1].find_all("td")
    date_text = clean(date_price_row[0].text)
    if "to" in date_text:
        open_date, close_date = map(
            str.strip, date_text.replace("Date:", "").split("to")
        )
        ipo["open_date"] = open_date + " 2025"
        ipo["close_date"] = close_date + " 2025"
    else:
        ipo["open_date"] = ipo["close_date"] = None

    price_band_text = clean(date_price_row[-1].text).replace("₹", "").replace("to", "-")
    price_parts = price_band_text.split("-")
    ipo["price"] = {
        "min": (
            int(price_parts[0].strip()) if price_parts[0].strip().isdigit() else None
        ),
        "max": (
            int(price_parts[1].strip())
            if len(price_parts) > 1 and price_parts[1].strip().isdigit()
            else None
        ),
    }

    # Last updated time in UTC
    updated_tag = block.find("p", class_="text-center")
    if updated_tag:
        local_time = datetime.strptime(
            clean(updated_tag.text).replace("Last updated on ", ""),
            "%d-%b-%Y %H:%M:%S",
        )
        utc_time = local_time.astimezone().astimezone(
            datetime.utcnow().astimezone().tzinfo
        )
        ipo["last_updated"] = utc_time.isoformat()
    else:
        ipo["last_updated"] = None

    # Parse subscription table
    subscription_data = parse_subscription_table(block)

    ipo["subscription_data"] = {
        "retail": {
            "QIBs": subscription_data.get("QIBs"),
            "Retail": subscription_data.get("Retail"),
            "HNIs": {
                "summary": subscription_data.get("HNIs"),
                "breakdown": subscription_data.get("breakdown", {}),
            },
        },
        "Employees": subscription_data.get("Employees"),
        "Shareholders": subscription_data.get("Shareholders"),
        "Total": subscription_data.get("Total"),
    }
    return ipo


def parse_subscription_table(block):
    def clean(text):
        return text.strip().replace("\xa0", " ").replace("\n", " ").strip()

    subscription_data = {
        "QIBs": None,
        "HNIs": None,
        "Retail": None,
        "Employees": None,
        "Shareholders": None,
        "Total": None,
        "breakdown": {},
    }
    all_tables = block.find_all("table")
    sub_table = None
    for t in all_tables:
        if (
            t.find("th")
            and "Category" in t.find("th").text
            and "Applied" in t.text
            and "Times" in t.text
        ):
            sub_table = t
            break
    if sub_table:
        rows = sub_table.find_all("tr")[1:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 4:
                category = clean(cols[0].text).replace(" ", " ").strip()
                offered = clean(cols[1].text)
                applied = clean(cols[2].text)
                times = clean(cols[3].text)
                record = {
                    "offered": offered,
                    "applied": applied,
                    "times": times,
                }
                if category == "QIBs":
                    subscription_data["QIBs"] = record
                elif category == "HNIs":
                    subscription_data["HNIs"] = record
                elif category == "Retail":
                    subscription_data["Retail"] = record
                elif category == "Employees":
                    subscription_data["Employees"] = record
                elif category == "Shareholders":
                    subscription_data["Shareholders"] = record
                elif category == "Total":
                    subscription_data["Total"] = record
                elif category.startswith("HNIs "):
                    subscription_data["breakdown"][category] = record
    return subscription_data
