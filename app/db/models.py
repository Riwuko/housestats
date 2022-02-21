from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import URLType

db = SQLAlchemy()
migrate = Migrate()


class House(db.Model):
    __tablename__ = "houses"
    __table_args__ = (db.UniqueConstraint("name", "website"),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    area = db.Column(db.Float, nullable=True)
    rooms_count = db.Column(db.Integer, nullable=True)
    building_type = db.Column(db.String(), nullable=True)
    price = db.Column(db.Float, nullable=False)
    website = db.Column(URLType, nullable=False)
    location_city = db.Column(db.String(), nullable=False)
    location_region = db.Column(db.String(), nullable=True)
    market = db.Column(db.Enum("Aftermarket", "Primary market", name="market_category"), nullable=True)

    def __repr__(self):
        return f'{self.id}: "{self.name}" ({self.rooms_count} pokoje) - {self.price} zł'
