import pandas as pd

from .base_house_loader import HouseLoader, HousesParameters


class AveragePricesParameters(HousesParameters):
    """Class for enum house parameters representing filtering values"""

    AVG_GROUP_BY = "avg_group_by"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class AverageHousesPricesLoader(HouseLoader):
    """Loads data from house table, calculate average prices and puts it into the DataFrame"""

    PARAMS = AveragePricesParameters

    def load_data(self, params: dict = None) -> dict:
        """Takes in params for filtering the data and returns filtered dataframe in a dict"""
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

    def _get_data_by_param(self, data: pd.DataFrame, param_name: str, param_val) -> pd.DataFrame:
        """Takes in param name and chooses appropriate filtering function"""
        return {
            self.PARAMS.PRICE_FROM: self._get_data_by_price_from,
            self.PARAMS.PRICE_TO: self._get_data_by_price_to,
            self.PARAMS.CITY: self._get_data_by_city,
            self.PARAMS.AREA: self._get_data_by_area,
        }.get(param_name)(data, param_val)

    def _get_data_between_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filters dataframe by start date and end date"""
        data = self._get_data_by_start_date(df)
        return self._get_data_by_end_date(data)

    def _get_data_by_start_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filters dateframe by start date (returns only records with datetime greater than start date)"""
        if not self._start_date:
            self._start_date = self.get_metadata().get(self.PARAMS.START_DATE)
        start_date = self._change_single_date_format(self._start_date)
        return df[(df["datetime"] >= start_date)]

    def _get_data_by_end_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filters dateframe by end date (returns only records with datetime less than end date)"""
        if not self._end_date:
            self._end_date = self.get_metadata().get(self.PARAMS.END_DATE)
        end_date = self._change_single_date_format(self._end_date)
        return df[(df["datetime"] <= end_date)]

    def _remove_edges_values_by_column(self, df, column) -> pd.DataFrame:
        """Removes from dataframe a given percentage of extreme values records"""
        PERCENT_VALUE = 5
        sorted_df = df.sort_values(by=column)
        min_position = int((len(sorted_df) / 100) * PERCENT_VALUE)
        max_position = int(len(sorted_df) - min_position)
        return sorted_df[min_position:max_position]

    def _calculate_average_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates price per meter column and the average price per meter for given time-unit"""
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

    def _get_unique_dates(self, df: pd.DataFrame) -> list:
        """Finds unique datetime values for given time-unit"""
        return {
            self.PARAMS.DAY: df.datetime.dt.date.unique().tolist(),
            self.PARAMS.WEEK: df.datetime.dt.strftime("%Y-%U").unique().tolist(),
            self.PARAMS.MONTH: df.datetime.dt.strftime("%Y-%m").unique().tolist(),
            self.PARAMS.YEAR: df.datetime.dt.year.unique().tolist(),
        }.get(self._average_by)

    def _change_df_date_format(self, df: pd.DataFrame) -> pd.Series:
        """Changes dataframe datetime column values for given time-unit"""
        return {
            self.PARAMS.DAY: df.datetime.dt.date,
            self.PARAMS.WEEK: df.datetime.dt.strftime("%Y-%U"),
            self.PARAMS.MONTH: df.datetime.dt.strftime("%Y-%m"),
            self.PARAMS.YEAR: df.datetime.dt.year,
        }.get(self._average_by)

    def _change_single_date_format(self, date):
        """Changes sigle date format for given time-unit"""
        return {
            self.PARAMS.DAY: pd.Timestamp(date),
            self.PARAMS.WEEK: pd.Timestamp(date).strftime("%Y-%U"),
            self.PARAMS.MONTH: pd.Timestamp(date).strftime("%Y-%m"),
            self.PARAMS.YEAR: pd.Timestamp(date).year,
        }.get(self._average_by)
