from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role          = db.Column(db.String(20), nullable=False, default='user')
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    reservations = db.relationship(
        'Reservation',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'

    id                  = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(128), nullable=False)
    price_per_hour      = db.Column(db.Float, nullable=False)
    address             = db.Column(db.String(256))
    pincode             = db.Column(db.String(10))
    total_spots         = db.Column(db.Integer, nullable=False)

    spots = db.relationship(
        'ParkingSpot',
        back_populates='lot',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<ParkingLot {self.prime_location_name} ({self.total_spots} spots)>"

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'

    id     = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(
        db.Integer,
        db.ForeignKey('parking_lots.id'),
        nullable=False
    )
    status = db.Column(db.String(1), nullable=False, default='A')

    lot          = db.relationship('ParkingLot', back_populates='spots')
    reservations = db.relationship(
        'Reservation',
        back_populates='spot',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<ParkingSpot {self.id} in Lot {self.lot_id} ({self.status})>"

class Reservation(db.Model):
    __tablename__ = 'reservations'

    id           = db.Column(db.Integer, primary_key=True)
    spot_id      = db.Column(
        db.Integer,
        db.ForeignKey('parking_spots.id'),
        nullable=False
    )
    user_id      = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    parked_at    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    left_at      = db.Column(db.DateTime)
    parking_cost = db.Column(db.Float)
    remarks      = db.Column(db.String(256))

    spot = db.relationship('ParkingSpot', back_populates='reservations')
    user = db.relationship('User', back_populates='reservations')

    def calculate_cost(self, rate_per_hour=None):
        """
        Compute parking_cost based on duration and rate_per_hour.
        Uses the lot's rate_per_hour if no override is provided.
        """
        if not self.left_at:
            return None
        duration = self.left_at - self.parked_at
        hours   = duration.total_seconds() / 3600
        rate    = rate_per_hour if rate_per_hour is not None else self.spot.lot.price_per_hour
        self.parking_cost = round(hours * rate, 2)
        return self.parking_cost

    def __repr__(self):
        return (
            f"<Reservation Spot:{self.spot_id} User:{self.user_id} "
            f"{self.parked_at}→{self.left_at}>"
        )