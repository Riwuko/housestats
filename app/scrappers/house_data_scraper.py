import bs4 as bs
from requests import get

from .house_detail_scraper import HouseDetailScraper


class HouseDataScraper:
    """Extracts data from the HTML of an url."""

    MAX_PAGE = 15

    def __init__(self, url: str) -> None:
        self._url = url
        self._detail_scraper = HouseDetailScraper()

    def scrap(self) -> list:
        """Scraps page data using pagination"""
        offers = []
        for page_num in range(1, self.MAX_PAGE):
            print(f"Scraping data from page {page_num}...")
            page = get(self._url, params={"page": page_num})
            parsed_page = bs.BeautifulSoup(page.content, "html.parser")
            offers += parsed_page.find_all("div", class_="offer-wrapper")
        return [self._get_offer_data(offer) for offer in offers]

    def _get_offer_data(self, offer: str) -> dict:
        """Takes in a offer parsed data and searches for needed tags"""
        name = offer.find("strong")
        price_text = offer.find("p", class_="price")
        footer = offer.find("td", class_="bottom-cell")
        footer_data = footer.find_all("small", class_="breadcrumb")
        location_text, date_time_text = footer_data

        hyperlink = offer.find("a")["href"]
        detail_data = self._detail_scraper.scrap_detail_house_data(hyperlink)

        return {
            "name": name,
            "price_text": price_text,
            "datetime_text": date_time_text,
            "location_text": location_text,
            "website": hyperlink,
            **detail_data,
        }
