from typing import Callable
from .db_tools import bulk_add, bulk_update, get_all, remove, remove_all
from .models import House

HOUSE_MODEL = House


def get_houses_by_name(houses: list) -> list:
    """Finds house objects by names"""
    houses_names = [house.get("name") for house in houses]
    return HOUSE_MODEL.query.filter(House.name.in_(houses_names)).all()


def prepare_houses_to_create(houses: list, existing_houses: list) -> list:
    """Returns only the houses that does not yet exist"""
    return [
        house
        for house in houses
        if not any(house["name"].lower() == existing_house.name.lower() for existing_house in existing_houses)
    ]


def prepare_houses_to_update(houses: list, existing_houses: list) -> list:
    """Returns only already existing houses"""
    houses_for_update = []
    for house in houses:
        for existing_house in existing_houses:
            if house["name"] == existing_house.name:
                house.update(vars(existing_house))
                houses_for_update.append(house)
                break
    return houses_for_update


def remove_duplicates(iterable: list, key: Callable = None) -> str:
    """Removes duplicated dicts from list of dicts"""
    if key is None:
        key = lambda x: x

    seen = set()
    for elem in iterable:
        k = key(elem)
        if k in seen:
            continue

        yield elem
        seen.add(k)


def add_new_houses(houses: list) -> list:
    """Takes in list of houses dicts and create/update (if existing) the house database"""
    existing_houses = get_houses_by_name(houses)
    houses_for_create = prepare_houses_to_create(houses, existing_houses)
    unique_houses = remove_duplicates(houses_for_create, lambda d: (d["name"], d["website"]))
    bulk_add(HOUSE_MODEL, unique_houses)

    houses_for_update = prepare_houses_to_update(houses, existing_houses)
    bulk_update(HOUSE_MODEL, houses_for_update)
    return get_houses_by_name(unique_houses)


def get_houses() -> list:
    """Returns all house records from db"""
    return get_all(HOUSE_MODEL)


def remove_all_houses() -> None:
    """Removes all house records from db"""
    remove_all(HOUSE_MODEL)


def remove_house_by_name(house_name: str) -> None:
    """Removes house from db by its name"""
    remove(HOUSE_MODEL, house_name)
