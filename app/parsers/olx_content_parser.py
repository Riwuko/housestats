import re
from datetime import datetime, timedelta

from babel.numbers import parse_decimal


class OLXContentParser:

    """
    ContentScraper class parses the data to declared format
    """

    TODAY = "dzisiaj"
    YESTERDAY = "wczoraj"
    AFTERMARKER = "Aftermarket"
    PRIMARY_MARKET = "Primary market"

    def __init__(self, olx_data):
        self._offers_list = olx_data

    def parse(self):
        return [self._parse_single_offer(data) for data in self._offers_list]

    def _params_to_text_decorator(func):
        def wrapper(self, offer):
            for k, v in offer.items():
                try:
                    offer[k] = v.get_text().strip()
                except AttributeError:
                    pass
            return func(self, offer=offer)

        return wrapper

    @_params_to_text_decorator
    def _parse_single_offer(self, offer):
        return {
            "price": parse_decimal(offer.get("price_text").replace("zł", "").replace(",", "."), locale="pl"),
            "datetime": self._parse_datetime(offer.get("datetime_text")),
            "location_city": self._parse_location(offer.get("location_text"))[0],
            "location_region": self._parse_location(offer.get("location_text"))[1],
            "area": self._parse_text_to_float(offer.get("area_text")),
            "rooms_count": self._parse_text_to_int(offer.get("rooms_count_text")),
            "website": offer.get("website"),
            "name": offer.get("name"),
            "building_type": re.sub("[^a-zA-Z]+", "", offer.get("building_type", "")),
            "market": self._parse_market_type(offer.get("market", "")),
        }

    def _parse_market_type(self, market_text):
        if not market_text:
            return None
        text = re.sub("[^a-zA-Z]+", "", market_text)
        if re.search(r"^w.*y$", text.lower()):
            return self.AFTERMARKER
        else:
            return self.PRIMARY_MARKET

    def _parse_location(self, location):
        location = location.split(",")
        city = location[0]
        try:
            region = location[1]
        except IndexError:
            region = None
        return city, region

    def _parse_text_to_float(self, text):
        return float("".join(filter(str.isdigit, text.replace(",", ".").replace("²", "")))) if text else None

    def _parse_text_to_int(self, text):
        return int("".join(filter(str.isdigit, text))) if text else None

    def _parse_datetime(self, date_data):
        date_core = date_data[:-6]
        day = {
            self.TODAY: datetime.now(),
            self.YESTERDAY: datetime.now() - timedelta(days=1),
        }.get(date_core)
        if day is not None:
            day = self._restore_time(day, date_data)
        else:
            day = self._get_datetime_by_month_text(date_data)
        return day

    def _restore_time(self, day, time_data):
        time = time_data[-5:]
        time = datetime.strptime(time, "%H:%M")
        return day.replace(hour=time.hour, minute=time.minute)

    def _get_datetime_by_month_text(self, month_text):
        month_string = {
            "sty": "january",
            "lut": "february",
            "mar": "march",
            "kwie": "april",
            "maj": "may",
            "cze": "june",
            "lip": "july",
            "sie": "august",
            "wrz": "september",
            "paź": "october",
            "lis": "november",
            "gru": "december",
        }.get(month_text[-3:])
        year = datetime.now().year
        day = month_text[:-4]
        date_string = f"{day} {month_string} {year}"
        return datetime.strptime(date_string, "%d %B %Y")
