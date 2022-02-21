from .models import db


def get_all(model):
    data = model.query.all()
    return data


def bulk_add(model, objects):
    objects = [model(**obj) for obj in objects]
    db.session.bulk_save_objects(objects)
    db.session.commit()


def bulk_update(model, objects):
    db.session.bulk_update_mappings(model, objects)
    db.session.commit()


def remove_all(model):
    db.session.query(model).delete()
    db.session.commit()


def remove(model, name):
    model.query.filter(model.name == name).delete()
    db.session.commit()
