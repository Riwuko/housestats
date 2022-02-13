from ctypes.wintypes import MAX_PATH
import re
import bs4 as bs
from requests import get

class OLXContentScraper:

    """
    ContentScraper class parses the HTML of a url to extract data.
    """
    OLX_URL = "www.olx.pl"
    AREA = "Powierzchnia"
    ROOMS = "Liczba pokoi"
    BUILDING = "Rodzaj zabudowy"
    MAX_PAGE = 30

    def __init__(self, url):
        self._url = url
    
    def scrap(self):
        offers = []
        for page_num in range(1, self.MAX_PAGE):
            print(f'Scraping data from page {page_num}...')
            page = get(self._url, params={'page': page_num})
            parsed_page = bs.BeautifulSoup(page.content, 'html.parser')
            offers += parsed_page.find_all('div', class_='offer-wrapper')
        return [self._get_offer_data(offer) for offer in offers]

    def _get_offer_data(self, offer):
        name = offer.find('strong')
        price_text = offer.find('p', class_='price')
        footer = offer.find('td', class_='bottom-cell')
        footer_data = footer.find_all('small', class_='breadcrumb')
        location_text, date_time_text = footer_data

        hyperlink = offer.find('a')['href']
        detail_data = self._get_offer_detail_data(hyperlink)

        return({
            "name": name,
            "price_text": price_text,
            "datetime_text": date_time_text,
            "location_text": location_text,
            "website": hyperlink,
            **detail_data
        })

    def _remove_substring(self, string, substring):
        return string.replace(substring, "") if string else None

    def _get_offer_detail_data(self, hyperlink):
        if not self.OLX_URL in hyperlink:
            return {}
        offer_page = get(hyperlink)
        parsed_page = bs.BeautifulSoup(offer_page.content, 'html.parser')
        area = parsed_page.find(text=re.compile(self.AREA))
        rooms_count = parsed_page.find(text=re.compile(self.ROOMS))
        building_type = parsed_page.find(text=re.compile(self.BUILDING))
        return {
            "area_text": self._remove_substring(area, self.AREA),
            "rooms_count_text": self._remove_substring(rooms_count, self.ROOMS),
            "building_type": self._remove_substring(building_type, self.BUILDING)
        }
