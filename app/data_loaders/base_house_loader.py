from datetime import date, timedelta

import pandas as pd
from db.house_tools import get_houses

from .base_loader import DataLoader


class HousesParameters:
    CITY = "city"
    START_DATE = "start_date"
    END_DATE = "end_date"
    PRICE_FROM = "price_from"
    PRICE_TO = "price_to"
    AREA = "area"


class HouseLoader(DataLoader):
    PARAMS = HousesParameters

    def load_data(self, params=None):
        self._data = self._get_data()

        data = self._data
        for param_name, param_val in params.items():
            data = self._get_data_by_param(data, param_name, param_val)
        return {
            "plain": data,
        }

    def get_metadata(self):
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

    def _get_data_by_param(self, data, param_name, param_val):
        return {
            self.PARAMS.START_DATE: self._get_data_by_start_date,
            self.PARAMS.END_DATE: self._get_data_by_end_date,
            self.PARAMS.CITY: self._get_data_by_city,
            self.PARAMS.PRICE_FROM: self._get_data_by_price_from,
            self.PARAMS.PRICE_TO: self._get_data_by_price_to,
            self.PARAMS.AREA: self._get_data_by_area,
        }.get(param_name)(data, param_val)

    def _get_data(self):
        return pd.DataFrame(h.__dict__ for h in get_houses())

    def _get_data_by_date(self, df, filter_date):
        return df[df["datetime"].dt.date == pd.Timestamp(filter_date)]

    def _get_date_from_param_or_meta(self, date, param_name):
        return date if date else self.get_metadata().get(param_name)

    def _get_data_by_start_date(self, df, start_date):
        start_date = self._get_date_from_param_or_meta(start_date, self.PARAMS.START_DATE)
        return df[(df["datetime"].dt.date >= pd.Timestamp(start_date))]

    def _get_data_by_end_date(self, df, end_date):
        end_date = self._get_date_from_param_or_meta(end_date, self.PARAMS.END_DATE)
        return df[(df["datetime"].dt.date <= pd.Timestamp(end_date))]

    def _get_data_by_city(self, df, cities):
        return df[df["location_city"].isin(cities)]

    def _get_data_by_price_from(self, df, price_from):
        return df[df["price"] >= price_from]

    def _get_data_by_price_to(self, df, price_to):
        return df[df["price"] <= price_to]

    def _get_data_by_area(self, df, area_range):
        mask = (df["area"] > float(area_range[0])) & (df["area"] <= float(area_range[1]))
        return df.loc[mask]
