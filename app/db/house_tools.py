from .models import House
from .db_tools import bulk_add, get_all, remove_all

HOUSE_MODEL = House

def get_houses_by_name(houses):
    houses_names = [house.get('name') for house in houses]
    return HOUSE_MODEL.query.filter(House.name.in_(houses_names)).all()

def prepare_houses_to_create(houses, existing_houses):
    return [house for house in houses 
    if not any(
        house['name'].lower() == existing_house.name.lower()
        for existing_house in existing_houses
    )]

def remove_duplicates(iterable, key=None):
    if key is None:
        key = lambda x: x

    seen = set()
    for elem in iterable:
        k = key(elem)
        if k in seen:
            continue

        yield elem
        seen.add(k)

def add_new_houses(houses):
    houses_for_update = get_houses_by_name(houses)
    houses_for_create = prepare_houses_to_create(houses, houses_for_update)
    unique_houses = remove_duplicates(houses_for_create, lambda d: (d["name"], d["datetime"]))
    bulk_add(HOUSE_MODEL, unique_houses)
    return get_houses_by_name(unique_houses)

def get_houses():
    return get_all(HOUSE_MODEL)

def remove_all_houses():
    HOUSE_MODEL.query.delete()
    remove_all(HOUSE_MODEL)
    
