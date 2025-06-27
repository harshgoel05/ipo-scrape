from flask import Config, Flask, request, jsonify
from flask_cors import CORS

from scraper_main import (
    get_all_ipo_listing_with_gmp_link,
    get_stock_details_and_gmp_from_symbol,
)

from dotenv import load_dotenv
from crawler_helper import scrape_page
from parse_subscription import parse_subscription_page

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config.from_object(Config)


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
    gmp_url = request.args.get("gmp_url")
    details_url = request.args.get("details_url")
    response = get_stock_details_and_gmp_from_symbol(details_url, gmp_url)
    return response


def clean(text):
    return text.strip().replace("\xa0", " ").replace("\n", " ").strip()


@app.route("/subscription")
def get_subscription():
    try:
        url = "https://ipopremium.in/view/subscription"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.1.0.000 Safari/537.36"
        }
        soup = scrape_page(url, headers=headers)
        if not soup:
            return jsonify({"error": "Failed to fetch subscription page"}), 500
        ipos = parse_subscription_page(soup)
        return jsonify(ipos)
    except Exception as e:
        app.logger.error(f"Error in get_subscription: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=8000)
