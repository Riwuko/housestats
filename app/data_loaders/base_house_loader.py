from datetime import date, timedelta

import pandas as pd
from db.house_tools import get_houses

from .base_loader import DataLoader


class HousesParameters:
    """Class for enum house parameters representing filtering values"""

    CITY = "city"
    START_DATE = "start_date"
    END_DATE = "end_date"
    PRICE_FROM = "price_from"
    PRICE_TO = "price_to"
    AREA = "area"


class HouseLoader(DataLoader):
    """Loads data from house table and puts it into the DataFrame"""

    PARAMS = HousesParameters
    _end_date = None
    _start_date = None

    def load_data(self, params: dict = None) -> dict:
        """Takes in params for filtering the data and returns filtered dataframe in a dict"""
        self._data = self._get_data()

        data = self._data
        for param_name, param_val in params.items():
            data = self._get_data_by_param(data, param_name, param_val)
        return {
            "plain": data,
        }

    def get_metadata(self) -> dict:
        """Calculates universal class metadata that does not depend on filtering params"""
        datetimes = self._data.datetime
        latest_date = datetimes.max().date()
        start_date = date.today() - timedelta(days=2)
        if not any(self._get_data_by_date(self._data, start_date)):
            start_date = latest_date

        return {
            "min-date": datetimes.min().date(),
            "max-date": latest_date,
            "start_date": start_date,
            "end_date": latest_date,
            "areas": self._data.area.notnull().unique(),
            "available_cities": self._data.location_city.unique(),
        }

    def _get_data_by_param(self, data: pd.DataFrame, param_name: str, param_val) -> pd.DataFrame:
        """Takes in param name and chooses appropriate filtering function"""
        return {
            self.PARAMS.START_DATE: self._get_data_by_start_date,
            self.PARAMS.END_DATE: self._get_data_by_end_date,
            self.PARAMS.CITY: self._get_data_by_city,
            self.PARAMS.PRICE_FROM: self._get_data_by_price_from,
            self.PARAMS.PRICE_TO: self._get_data_by_price_to,
            self.PARAMS.AREA: self._get_data_by_area,
        }.get(param_name)(data, param_val)

    def _get_data(self) -> pd.DataFrame:
        """Loads data into the dataframe"""
        return pd.DataFrame(h.__dict__ for h in get_houses())

    def _get_data_by_date(self, df: pd.DataFrame, filter_date: str) -> pd.DataFrame:
        """Filters dataframe by date"""
        return df[df["datetime"].dt.date == pd.Timestamp(filter_date)]

    def _get_data_by_start_date(self, df: pd.DataFrame, start_date: str) -> pd.DataFrame:
        """Filters dateframe by start date (returns only records with datetime greater than start date)"""
        if not self._start_date and not start_date:
            self._start_date = self.get_metadata().get(self.PARAMS.START_DATE)
        elif not self._start_date:
            self._start_date = start_date
        return df[(df["datetime"].dt.date >= pd.Timestamp(self._start_date))]

    def _get_data_by_end_date(self, df: pd.DataFrame, end_date: str) -> pd.DataFrame:
        """Filters dateframe by end date (returns only records with datetime less than end date)"""
        if not self._end_date and not end_date:
            self._end_date = self.get_metadata().get(self.PARAMS.END_DATE)
        elif not self._end_date:
            self._end_date = end_date
        return df[(df["datetime"].dt.date <= pd.Timestamp(self._end_date))]

    def _get_data_by_city(self, df: pd.DataFrame, cities: list) -> pd.DataFrame:
        """Filters dateframe by city"""
        return df[df["location_city"].isin(cities)]

    def _get_data_by_price_from(self, df: pd.DataFrame, price_from: float) -> pd.DataFrame:
        """Filters dateframe by price from (returns only records with price greater than price from)"""
        return df[df["price"] >= price_from]

    def _get_data_by_price_to(self, df: pd.DataFrame, price_to: float) -> pd.DataFrame:
        """Filters dateframe by price to (returns only records with price less than price to)"""
        return df[df["price"] <= price_to]

    def _get_data_by_area(self, df: pd.DataFrame, area_range: tuple) -> pd.DataFrame:
        """Filters dateframe by area range"""
        mask = (df["area"] > float(area_range[0])) & (df["area"] <= float(area_range[1]))
        return df.loc[mask]
