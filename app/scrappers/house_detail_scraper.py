import re
import bs4 as bs
from abc import ABC
from requests import get


class HouseDetailStrategy(ABC):
    """Abstract strategy class that scraps house offer detail data with BeautifulSoup"""

    HOUSE_DATA = {}
    AREA = "Powierzchnia"
    ROOMS = "Liczba pokoi"
    BUILDING = "Rodzaj zabudowy"
    MARKET = "Rynek"

    def get_data(self, hyperlink: str) -> dict:
        """Takes in a hyperlink, scraps data, pre-prepares it and returns it as a dict"""
        offer_page = get(hyperlink)
        parsed_page = bs.BeautifulSoup(offer_page.content, "html.parser")
        data = self._scrap_data(parsed_page)
        return {
            "area_text": self._remove_substring(data["area"], self.AREA),
            "rooms_count_text": self._remove_substring(data["rooms_count"], self.ROOMS),
            "building_type": self._remove_substring(data["building_type"], self.BUILDING),
            "market": self._remove_substring(data["market"], self.MARKET),
        }

    def _scrap_data(self, parsed_page: str) -> dict:
        """Concrete function that can scrap web page data"""
        raise NotImplementedError

    def _remove_substring(self, string: str, substring: str) -> str:
        """Finds substring in a string and removes it"""
        return string.replace(substring, "") if string else ""


class OlxHouseDetailStrategy(HouseDetailStrategy):
    """Scraper for OLX house offer detail web page"""

    def _scrap_data(self, parsed_page: str) -> dict:
        return {
            "area": parsed_page.find(text=re.compile(self.AREA)),
            "rooms_count": parsed_page.find(text=re.compile(self.ROOMS)),
            "market": parsed_page.find(text=re.compile(self.MARKET)),
            "building_type": parsed_page.find(text=re.compile(self.BUILDING)),
        }


class OtodomHouseDetailStrategy(HouseDetailStrategy):
    """Scraper for Otodom house offer detail web page"""

    def _scrap_data(self, parsed_page: str) -> dict:
        area = parsed_page.find("div", {"aria-label": self.AREA})
        rooms = parsed_page.find("div", {"aria-label": self.ROOMS})
        market = parsed_page.find("div", {"aria-label": self.MARKET})
        building = parsed_page.find("div", {"aria-label": self.BUILDING})
        return {
            "area": area.get_text() if area else "",
            "rooms_count": rooms.get_text() if rooms else "",
            "market": market.get_text() if market else "",
            "building_type": building.get_text() if building else "",
        }


class HouseDetailScraper:
    """Uses scraping strategy based on URL and returns scraped data"""

    OTODOM_URL = "www.otodom.pl"
    OLX_URL = "www.olx.pl"

    def scrap_detail_house_data(self, hyperlink: str) -> dict:
        """Takes in a house offer hyperlink, returns scraped data"""
        domain = self._get_domain_from_hyperlink(hyperlink)
        scraping_strategy = self._get_strategy(domain)
        return scraping_strategy.get_data(hyperlink)

    def _get_domain_from_hyperlink(self, hyperlink: str) -> str:
        """Takes in a house offer hyperlink and return its domain"""
        return self.OLX_URL if self.OLX_URL in hyperlink else self.OTODOM_URL

    def _get_strategy(self, domain: str) -> HouseDetailStrategy:
        """Gets a domain and returns appropriate scraping class instance"""
        return {
            self.OLX_URL: OlxHouseDetailStrategy(),
            self.OTODOM_URL: OtodomHouseDetailStrategy(),
        }.get(domain)
