import pandas as pd

from .base_house_loader import HouseLoader


class CityHousesLoader(HouseLoader):

    def load_data(self, params=None):
        data = super().load_data(params).get("plain")
        
        return {
            "plain": data.sort_values(by='datetime'),
            }


    def _get_data(self):
        df = super()._get_data()
        df["price_mk"] = self._calculate_price_per_meter(df)
        return df
    
    def _calculate_price_per_meter(self, df):
        return pd.to_numeric(df['price'])/pd.to_numeric(df['area'])
