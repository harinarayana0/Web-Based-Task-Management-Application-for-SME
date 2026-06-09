"""
Database models for ServiceLink application.

This module defines the database schema using SQLAlchemy ORM.
Models include User, Service, Booking, and Review.

Design decisions:
- Using timestamps for audit trails
- Cascading deletes to maintain referential integrity
- Indexing on frequently queried columns (location, category, status)
- Separate role field instead of role table for simplicity
"""

from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """
    User model for both clients and service providers.
    
    Attributes:
        id: Primary key
        username: Unique username for login
        email: Unique email address
        password_hash: Hashed password (never store plain text)
        role: Either 'client' or 'provider'
        location: User's location for service matching
        phone: Contact phone number
        bio: User description (mainly for providers)
        created_at: Timestamp of account creation
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')  # 'client' or 'provider'
    location = db.Column(db.String(100), index=True)
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    # Services provided (if user is a provider)
    services = db.relationship('Service', backref='provider', lazy='dynamic', cascade='all, delete-orphan')
    
    # Bookings made (if user is a client)
    bookings_made = db.relationship('Booking', foreign_keys='Booking.client_id',
                                    backref='client', lazy='dynamic', cascade='all, delete-orphan')
    
    # Bookings received (if user is a provider, through services)
    # Reviews given
    reviews_given = db.relationship('Review', foreign_keys='Review.client_id',
                                   backref='client', lazy='dynamic', cascade='all, delete-orphan')
    
    # Reviews received (if user is a provider)
    reviews_received = db.relationship('Review', foreign_keys='Review.provider_id',
                                      backref='provider', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Hash and set the user's password.
        Uses Werkzeug's security functions for secure hashing.
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify a password against the stored hash.
        
        Args:
            password (str): Plain text password to verify
        
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def get_average_rating(self):
        """
        Calculate average rating for a service provider.
        
        Returns:
            float: Average rating (0 if no reviews)
        """
        if self.role != 'provider':
            return 0
        
        reviews = self.reviews_received.all()
        if not reviews:
            return 0
        
        return sum(review.rating for review in reviews) / len(reviews)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Service(db.Model):
    """
    Service model representing services offered by providers.
    
    Attributes:
        id: Primary key
        provider_id: Foreign key to User
        service_name: Name of the service
        description: Detailed description
        category: Service category (cleaning, handyman, tutoring, etc.)
        price: Service price per hour/session
        created_at: Timestamp of service creation
    """
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='service', lazy='dynamic', cascade='all, delete-orphan')
    availability_slots = db.relationship('AvailabilitySlot', backref='service',
                                        lazy='dynamic', cascade='all, delete-orphan')
    
    def get_average_rating(self):
        """
        Calculate average rating for this service based on completed bookings.
        
        Returns:
            float: Average rating (0 if no reviews)
        """
        completed_bookings = self.bookings.filter_by(status='completed').all()
        reviews = [booking.review for booking in completed_bookings if booking.review]
        
        if not reviews:
            return 0
        
        return sum(review.rating for review in reviews) / len(reviews)
    
    def __repr__(self):
        return f'<Service {self.service_name}>'


class AvailabilitySlot(db.Model):
    """
    Availability slots for services.
    Providers can set when they are available to provide services.
    
    Attributes:
        id: Primary key
        service_id: Foreign key to Service
        date: Date of availability
        start_time: Start time of slot
        end_time: End time of slot
        is_booked: Whether slot is already booked
    """
    __tablename__ = 'availability_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f'<AvailabilitySlot {self.date} {self.start_time}-{self.end_time}>'


class Booking(db.Model):
    """
    Booking model representing service bookings.
    
    Attributes:
        id: Primary key
        client_id: Foreign key to User (client)
        service_id: Foreign key to Service
        slot_id: Foreign key to AvailabilitySlot
        booking_date: Date of the booking
        start_time: Start time of booking
        end_time: End time of booking
        status: Booking status (pending, confirmed, completed, cancelled)
        notes: Additional notes from client
        created_at: Timestamp of booking creation
    """
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False, index=True)
    slot_id = db.Column(db.Integer, db.ForeignKey('availability_slots.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    slot = db.relationship('AvailabilitySlot', backref='booking', uselist=False)
    review = db.relationship('Review', backref='booking', uselist=False, cascade='all, delete-orphan')
    
    def can_be_reviewed(self):
        """
        Check if this booking can be reviewed.
        Only completed bookings can be reviewed.
        
        Returns:
            bool: True if can be reviewed, False otherwise
        """
        return self.status == 'completed' and self.review is None
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'


class Review(db.Model):
    """
    Review model for client reviews of service providers.
    
    Attributes:
        id: Primary key
        booking_id: Foreign key to Booking (one review per booking)
        client_id: Foreign key to User (reviewer)
        provider_id: Foreign key to User (reviewee)
        rating: Rating from 1 to 5
        comment: Text review
        created_at: Timestamp of review creation
    """
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, unique=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Review {self.id} - Rating: {self.rating}>'
