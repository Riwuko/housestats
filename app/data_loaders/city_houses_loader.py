import pandas as pd

from .base_loader import DataLoader
from db.house_tools import get_houses
from datetime import timedelta, date

class CityHousesLoaderParameters():
    CITY = "city"
    STAR_DATE = "start_date"
    END_DATE = "end_date"
    PRICE_FROM = "price_from"
    PRICE_TO = "price_to"

class CityHousesLoader(DataLoader):
    PARAMS = CityHousesLoaderParameters

    def load_data(self, params):
        self._data = self._get_data()

        data = self._data
        data["datetime"] = pd.to_datetime(data.datetime)
        for param_name, param_val in params.items():
            data = self._get_data_by_param(data, param_name, param_val)

        return {
            "plain": data,
            "date_sorted": data.sort_values(by='datetime'),
            }

    def get_metadata(self):
        datetimes = self._data.datetime
        latest_date = datetimes.max().date()
        start_date = date.today() - timedelta(days=2)
        if not any (self._get_data_by_date(self._data, start_date)):
            start_date = latest_date
        
        return {
            "min-date": datetimes.min().date(),
            "max-date": latest_date,
            "start_date": start_date,
            "end_date": latest_date,
            "available_cities": self._data.location_city.unique(),
        }

    def _get_data_by_param(self, data, param_name, param_val):
        return {
            self.PARAMS.CITY: self._get_data_by_city,
            self.PARAMS.STAR_DATE: self._get_data_by_start_date,
            self.PARAMS.END_DATE: self._get_data_by_end_date,
            self.PARAMS.PRICE_FROM: self._get_data_by_price_from,
            self.PARAMS.PRICE_TO: self._get_data_by_price_to,
        }.get(param_name)(data, param_val)

    def _get_data(self):
        return pd.DataFrame(h.__dict__ for h in get_houses())

    def _get_data_by_date(self, df, filter_date):
        return df[df["datetime"] == pd.Timestamp(filter_date)]

    def _get_date_from_param_or_meta(self, date, param_name):
        return date if date else self.get_metadata().get(param_name)

    def _get_data_by_start_date(self, df, start_date):
        start_date = self._get_date_from_param_or_meta(start_date, "start_date")
        return df[(df['datetime'] >= pd.Timestamp(start_date))]
    
    def _get_data_by_end_date(self, df, end_date):
        end_date = self._get_date_from_param_or_meta(end_date, "end_date")
        return df[(df['datetime'] <= pd.Timestamp(end_date))]

    def _get_data_by_city(self, df, cities):
        return df[df["location_city"].isin(cities)]

    def _get_data_by_price_from(self, df, price_from):
        return df[df["price"]>=price_from]
        
    def _get_data_by_price_to(self, df, price_to):
        return df[df["price"]<=price_to]
