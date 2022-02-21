import re

import bs4 as bs
from requests import get


class HouseDetailScraper:
    OTODOM_URL = "www.otodom.pl"
    OLX_URL = "www.olx.pl"

    def scrap_detail_house_data(self, hyperlink):
        domain = self._get_domain_from_hyperlink(hyperlink)
        scraping_strategy = self._get_strategy(domain)
        return scraping_strategy.get_data(hyperlink)

    def _get_domain_from_hyperlink(self, hyperlink):
        return self.OLX_URL if self.OLX_URL in hyperlink else self.OTODOM_URL

    def _get_strategy(self, domain):
        return {
            self.OLX_URL: OlxHouseDetailStrategy(),
            self.OTODOM_URL: OtodomHouseDetailStrategy(),
        }.get(domain)


class HouseDetailStrategy:
    HOUSE_DATA = {}
    AREA = "Powierzchnia"
    ROOMS = "Liczba pokoi"
    BUILDING = "Rodzaj zabudowy"
    MARKET = "Rynek"

    def get_data(self, hyperlink):
        offer_page = get(hyperlink)
        parsed_page = bs.BeautifulSoup(offer_page.content, "html.parser")
        data = self._scrap_data(parsed_page)
        return {
            "area_text": self._remove_substring(data["area"], self.AREA),
            "rooms_count_text": self._remove_substring(data["rooms_count"], self.ROOMS),
            "building_type": self._remove_substring(data["building_type"], self.BUILDING),
            "market": self._remove_substring(data["market"], self.MARKET),
        }

    def _scrap_data(self, parsed_page):
        raise NotImplementedError

    def _remove_substring(self, string, substring):
        return string.replace(substring, "") if string else ""


class OlxHouseDetailStrategy(HouseDetailStrategy):
    def _scrap_data(self, parsed_page):
        return {
            "area": parsed_page.find(text=re.compile(self.AREA)),
            "rooms_count": parsed_page.find(text=re.compile(self.ROOMS)),
            "market": parsed_page.find(text=re.compile(self.MARKET)),
            "building_type": parsed_page.find(text=re.compile(self.BUILDING)),
        }


class OtodomHouseDetailStrategy(HouseDetailStrategy):
    def _scrap_data(self, parsed_page):
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
