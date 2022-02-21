from abc import ABC, abstractmethod


class BasePage(ABC):
    data_loader = None
    dataframe = None
    params = {}

    @classmethod
    def load_data(cls):
        cls.dataframe = cls.data_loader.load_data(cls.params)

    @classmethod
    @abstractmethod
    def layout(cls, params):
        pass

    @classmethod
    @abstractmethod
    def register_callbacks(cls, app):
        pass

    @classmethod
    def _update_param(cls, name, value):
        cls.params[name] = value
        cls.load_data()
