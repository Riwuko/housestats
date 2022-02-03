from .models import db
from sqlalchemy.dialects.postgresql import insert

def get_all(model):
    data = model.query.all()
    return data


def bulk_add(model, objects):
    [db.session.add(model(**obj)) for obj in objects]
    db.session.commit()


def remove_all(model):
    db.session.query(model).delete()
    db.session.commit()
