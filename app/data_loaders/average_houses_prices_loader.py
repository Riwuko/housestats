from datetime import date, timedelta

import pandas as pd

from .base_house_loader import HouseLoader, HousesParameters


class AveragePricesParameters(HousesParameters):
    AVG_GROUP_BY = "avg_group_by"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class AverageHousesPricesLoader(HouseLoader):
    PARAMS = AveragePricesParameters
    _end_date = None
    _start_date = None

    def load_data(self, params=None):
        self._start_date = params.pop(self.PARAMS.START_DATE, self._start_date)
        self._end_date = params.pop(self.PARAMS.END_DATE, self._end_date)
        self._average_by = params.pop(self.PARAMS.AVG_GROUP_BY, self.PARAMS.DAY)

        data = super().load_data(params).get("plain")
        aftermarkets = data[data.market == "Aftermarket"]
        primarymarkets = data[data.market == "Primary market"]

        aftermarkets = self._calculate_average_prices(aftermarkets)
        primarymarkets = self._calculate_average_prices(primarymarkets)

        aftermarkets = self._get_data_between_dates(aftermarkets)
        primarymarkets = self._get_data_between_dates(primarymarkets)

        return {
            "plain": data,
            "primary_market_data": primarymarkets.sort_values(by="datetime"),
            "aftermarket_data": aftermarkets.sort_values(by="datetime"),
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
            self.PARAMS.PRICE_FROM: self._get_data_by_price_from,
            self.PARAMS.PRICE_TO: self._get_data_by_price_to,
            self.PARAMS.CITY: self._get_data_by_city,
            self.PARAMS.AREA: self._get_data_by_area,
        }.get(param_name)(data, param_val)

    def _get_data_between_dates(self, df):
        data = self._get_data_by_start_date(df)
        return self._get_data_by_end_date(data)

    def _get_data_by_start_date(self, df):
        if not self._start_date:
            self._start_date = self.get_metadata().get(self.PARAMS.START_DATE)
        start_date = self._change_single_date_format(self._start_date)
        return df[(df["datetime"] >= start_date)]

    def _get_data_by_end_date(self, df):
        if not self._end_date:
            self._end_date = self.get_metadata().get(self.PARAMS.END_DATE)
        end_date = self._change_single_date_format(self._end_date)
        return df[(df["datetime"] <= end_date)]

    def _remove_edges_values_by_column(self, df, column):
        PERCENT_VALUE = 5
        sorted_df = df.sort_values(by=column)
        min_position = int((len(sorted_df) / 100) * PERCENT_VALUE)
        max_position = int(len(sorted_df) - min_position)
        return sorted_df[min_position:max_position]

    def _calculate_average_prices(self, df):
        df = df.dropna(subset=["price", "area"])
        df = self._remove_edges_values_by_column(df, "price")
        df["price_mk"] = pd.to_numeric(df["price"]) / pd.to_numeric(df["area"])
        unique_dates = self._get_unique_dates(df)
        df["datetime"] = self._change_df_date_format(df)
        averages = [
            {
                "datetime": day,
                "price_mk": round(sum(df[df["datetime"] == day].price_mk) / len(df[df["datetime"] == day]), 2),
                "location_city": df[df["datetime"] == day].location_city,
            }
            for day in unique_dates
        ]
        return pd.DataFrame(averages)

    def _get_unique_dates(self, df):
        return {
            self.PARAMS.DAY: df.datetime.dt.date.unique().tolist(),
            self.PARAMS.WEEK: df.datetime.dt.strftime("%Y-%U").unique().tolist(),
            self.PARAMS.MONTH: df.datetime.dt.strftime("%Y-%m").unique().tolist(),
            self.PARAMS.YEAR: df.datetime.dt.year.unique().tolist(),
        }.get(self._average_by)

    def _change_df_date_format(self, df):
        return {
            self.PARAMS.DAY: df.datetime.dt.date,
            self.PARAMS.WEEK: df.datetime.dt.strftime("%Y-%U"),
            self.PARAMS.MONTH: df.datetime.dt.strftime("%Y-%m"),
            self.PARAMS.YEAR: df.datetime.dt.year,
        }.get(self._average_by)

    def _change_single_date_format(self, date):
        return {
            self.PARAMS.DAY: pd.Timestamp(date),
            self.PARAMS.WEEK: pd.Timestamp(date).strftime("%Y-%U"),
            self.PARAMS.MONTH: pd.Timestamp(date).strftime("%Y-%m"),
            self.PARAMS.YEAR: pd.Timestamp(date).year,
        }.get(self._average_by)
