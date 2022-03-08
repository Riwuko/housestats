import pandas as pd

from .base_house_loader import HouseLoader


class CityHousesLoader(HouseLoader):
    """Loads data from house table and puts it into the DataFrame"""

    def load_data(self, params: dict = None) -> dict:
        """Takes in params for filtering the data and returns filtered dataframe in a dict"""
        data = super().load_data(params).get("plain")

        return {
            "plain": data.sort_values(by="datetime"),
        }

    def _get_data(self) -> pd.DataFrame:
        """Takes params for loading the data, add additional price column and returns it as a dict"""
        df = super()._get_data()
        df = df.dropna(subset=["price", "area", "market"])
        df["price_mk"] = self._calculate_price_per_meter(df)
        return df

    def _calculate_price_per_meter(self, df: pd.DataFrame) -> pd.Series:
        """Calculates price per meter for every dataframe record"""
        return pd.to_numeric(df["price"]) / pd.to_numeric(df["area"])
