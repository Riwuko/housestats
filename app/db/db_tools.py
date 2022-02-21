from .models import db


def get_all(model) -> list:
    """Returns all model records from db"""
    return model.query.all()


def bulk_add(model, objects: list) -> None:
    """Takes in list of dicts to create model instances and bulk saves them"""
    objects = [model(**obj) for obj in objects]
    db.session.bulk_save_objects(objects)
    db.session.commit()


def bulk_update(model, objects: list) -> None:
    """Takes in list of dicts to bulk update existing records"""
    db.session.bulk_update_mappings(model, objects)
    db.session.commit()


def remove_all(model) -> None:
    """Removes all model records from db"""
    db.session.query(model).delete()
    db.session.commit()


def remove(model, name):
    """Removes single model record by its name from db"""
    model.query.filter(model.name == name).delete()
    db.session.commit()
