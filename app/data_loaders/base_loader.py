from abc import ABC, abstractmethod


class DataLoader(ABC):
    def __init__(self) -> None:
        self._data = None

    @abstractmethod
    def load_data(self, params: dict = {}) -> dict:
        pass
