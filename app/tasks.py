from db.house_tools import add_new_houses
from parsers import OLXContentParser
from scrappers import HouseDataScraper

from app import celery


@celery.task()
def download_olx_houses():
    scraped_data = HouseDataScraper(
        "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/wielkopolskie/?search%5Bfilter_float_price%3Ato%5D=1000000/"
    ).scrap()
    data = OLXContentParser(scraped_data).parse()
    print(add_new_houses(data))
