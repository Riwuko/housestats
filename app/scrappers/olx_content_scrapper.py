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

    def __init__(self, url):
        self._url = url
    
    def scrap(self):
        page = get(self._url)
        parsed_page = bs.BeautifulSoup(page.content, 'html.parser')
        offers = parsed_page.find_all('div', class_='offer-wrapper')
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

    def _get_offer_detail_data(self, hyperlink):
        if not self.OLX_URL in hyperlink:
            return {}
        offer_page = get(hyperlink)
        parsed_page = bs.BeautifulSoup(offer_page.content, 'html.parser')
        area = parsed_page.find(text=re.compile(self.AREA))
        rooms_count = parsed_page.find(text=re.compile(self.ROOMS))
        building_type = parsed_page.find(text=re.compile(self.BUILDING))
        return {
            "area_text": area.replace(self.AREA, ""),
            "rooms_count_text": rooms_count.replace(self.ROOMS, ""),
            "building_type": building_type.replace(self.BUILDING, "")
        }
