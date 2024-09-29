from glob import escape
from flask import Flask, request

from scraper_main import get_all_ipo_listing_with_gmp_link, get_stock_details_and_gmp_from_symbol

app = Flask(__name__)

# ------------------------------------------------
# GET /calendar
# Returns the IPO calendar with GMP links
# ------------------------------------------------
@app.route("/calendar")
def get_calendar():
    return get_all_ipo_listing_with_gmp_link()

# ------------------------------------------------
# GET /details/<symbol>
# @param symbol - Stock symbol
# @param gmp_url - GMP URL (Query Param)
# Returns the IPO details and GMP timeline for a given symbol
@app.route("/details")
def get_ipo_details_by_symbol():
    gmp_url = request.args.get('gmp_url')
    details_url = request.args.get('details_url')
    return get_stock_details_and_gmp_from_symbol(details_url, gmp_url)

