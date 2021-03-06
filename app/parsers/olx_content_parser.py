import re
from datetime import datetime, timedelta

from babel.numbers import parse_decimal


class OLXContentParser:
    """Parses the data to declared format"""

    TODAY = "dzisiaj"  # related to the specifics of the used webpages
    YESTERDAY = "wczoraj"
    AFTERMARKER = "Aftermarket"
    PRIMARY_MARKET = "Primary market"

    def __init__(self, olx_data: list) -> None:
        self._offers_list = olx_data

    def parse(self) -> list:
        """Parses all offers from the offer list in a loop"""
        return [self._parse_single_offer(data) for data in self._offers_list]

    def _params_to_text_decorator(func):
        """Takes in a offer dict and changes items values to text format"""

        def wrapper(self, offer: dict) -> dict:
            for k, v in offer.items():
                try:
                    offer[k] = v.get_text().strip()
                except AttributeError:
                    pass
            return func(self, offer=offer)

        return wrapper

    @_params_to_text_decorator
    def _parse_single_offer(self, offer: dict) -> dict:
        """Takes in raw data and parses it to the required format"""
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

    def _parse_market_type(self, market_text: str) -> str:
        """Checks which market type represents selected item"""
        if not market_text:
            return None
        text = re.sub("[^a-zA-Z]+", "", market_text)
        if re.search(r"^w.*y$", text.lower()):
            return self.AFTERMARKER
        else:
            return self.PRIMARY_MARKET

    def _parse_location(self, location: str) -> tuple:
        """Takes in location and splits it into city and region"""
        location = location.split(",")
        city = location[0]
        try:
            region = location[1]
        except IndexError:
            region = None
        return city, region

    def _parse_text_to_float(self, text: str) -> float:
        """Returns text as corresponding float"""
        return float("".join(filter(str.isdigit, text.replace(",", ".").replace("²", "")))) if text else None

    def _parse_text_to_int(self, text: str) -> int:
        """Returns text as corresponding int"""
        return int("".join(filter(str.isdigit, text))) if text else None

    def _parse_datetime(self, date_data: str) -> datetime:
        """Takes in date as string and searches for patterns that allows to parse it to a datetime"""
        date_core = date_data[:-6]
        day = {
            self.TODAY: datetime.now(),
            self.YESTERDAY: datetime.now() - timedelta(days=1),
        }.get(date_core)
        if day is not None:
            day = self._restore_time(day, date_data)  # restore lost time information
        else:
            day = self._get_datetime_by_month_text(date_data)
        return day

    def _restore_time(self, day: str, time_data: datetime) -> datetime:
        """Takes in day data and its original time-string and converts it to a datetime"""
        time = time_data[-5:]
        time = datetime.strptime(time, "%H:%M")
        return day.replace(hour=time.hour, minute=time.minute)

    def _get_datetime_by_month_text(self, month_text: str) -> datetime:
        """Takes month text in polish and searches for english substitute to convert it into a datetime"""
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
