from crawler_helper import scrape_page
from helper import convert_to_iso_format, convert_to_slug, parse_lot_size, process_ipo_date, process_listing_date

import re

def get_full_ipo_details(stock):
    try:
        return process_individual_stock(stock)
    except Exception as e:
        print(f"Error reading individual stock data: {stock['symbol']}")
        print(e)
        return None

def process_individual_stock(individual_stock):
    link = individual_stock['link']
    data = scrape_page(link)
    ipo_meta = data.find('div', class_='ipo-meta')

    listing_date = ipo_meta.find_all('div', class_='four columns')[1].find('div', class_='value').text.strip()
    if(listing_date == '-'):
        listing_date = None
    price_range = ipo_meta.find_all('div', class_='three columns')[0].find('div', class_='value').text.strip()
    issue_size = ipo_meta.find_all('div', class_='two columns')[0].find('div', class_='value').text.strip()
    if(issue_size == '\u2013'):
        issue_size = None

    # Extracting lot size, if available
    lot_size_info = ipo_meta.find_all('div', class_='three columns')[0].find('div', class_='text-12')
    if(lot_size_info):
        lot_size_str = lot_size_info.text.strip() if lot_size_info else "Not available"
        lot_size,min_investment =  parse_lot_size(lot_size_str)
    else:
        lot_size = None
        min_investment = None

    # Extract IPO Schedule
    ipo_schedule = data.find('table', class_='ipo-schedule')
    if not ipo_schedule:
        schedule = []
    else:
        schedule_rows = ipo_schedule.find_all('tr')
        schedule = []
        for row in schedule_rows:
            label = row.find('td', class_='ipo-schedule-label').text.strip()
            date = convert_to_iso_format(row.find('td', class_='ipo-schedule-date').text.strip())
            schedule_temp = {}
            schedule_temp["event"] = convert_to_slug(label)
            schedule_temp["date"] = date
            schedule_temp["eventTitle"] = label
            schedule.append(schedule_temp)


    # Extract Company Information
    ipo_section = data.find('section', id='ipo')
    rows = ipo_section.find_all('div', class_='row')
    six_columns = rows[len(rows)-1].find_all('div', class_='six columns')
    about_section_str = six_columns[len(six_columns)-1].find('p')
    if not about_section_str:
        content_text = []
        content_rows = ipo_section.find('div', class_='mini-container')
        content_p = content_rows.find_all('p')
        for p in content_p:
            text = p.text
            if text:
                content_text.append(text)
        about_section = " /n ".join(content_text)
    else:
        about_section = about_section_str.text
    # ipo_date = ipo_meta.find('div', class_='four columns').find('div', class_='value').text.strip()
    # if(ipo_date == 'To be announced'):
    #     ipo_start_date = None
    #     ipo_end_date = None
    # else:
    #     ipo_start_date, ipo_end_date = process_ipo_date(ipo_date)
    # price_range_list = re.findall(r'\d+', price_range)
    # if len(price_range_list) != 0:
    #     min_price = re.findall(r'\d+', price_range)[0]
    #     max_price = re.findall(r'\d+', price_range)[1]
    # else:
    #     min_price = None
    #     max_price = None

    # if listing_date:
    #     listing_date = process_listing_date(listing_date)
    # else:
    #     listing_date = None

    strengths = []
    strengths_header = data.find('h3', text='Strengths') or data.find('h2', text='Strengths') 
    if strengths_header:
        strengths_list = strengths_header.find_next('ul') 
        strengths = [li.text for li in strengths_list.find_all('li')]

    # Extract risks
    risks = []
    risks_header = data.find('h3', text='Risks')  or data.find('h2', text='Risks') 
    if risks_header:
        risks_list = risks_header.find_next('ul')
        risks = [li.text for li in risks_list.find_all('li')]
    data = {
        # 'ipo_start_date': ipo_start_date,
        # 'ipo_end_date': ipo_end_date,
        # 'listing_date':listing_date,
        # 'min_price': min_price,
        # 'max_price': max_price,
        'issueSize': issue_size,
        'sizePerLot': lot_size,
        'schedule': schedule,
        'about': about_section,
        'min_investment' : min_investment,
        'strengths': strengths,
        'risks': risks
    }
    return data