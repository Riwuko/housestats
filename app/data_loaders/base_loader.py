from abc import ABC, abstractmethod


class DataLoader(ABC):
    """Abstract class that loads data into the pandas DataFrames"""

    def __init__(self) -> None:
        self._data = None

    @abstractmethod
    def load_data(self, params: dict = None) -> dict:
        """Takes params for loading the data and returns it as a dict"""
        raise NotImplementedError
