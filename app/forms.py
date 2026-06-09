"""
Flask-WTF forms for ServiceLink application.

This module defines all forms used in the application with validation.
Forms include registration, login, service creation, booking, and reviews.

Design decisions:
- Using Flask-WTF for CSRF protection
- Comprehensive validation to ensure data integrity
- Custom validators for business logic
"""

from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, TextAreaField, SelectField,
                     FloatField, DateField, TimeField, IntegerField, BooleanField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length, 
                                ValidationError, NumberRange, Optional)
from app.models import User


class RegistrationForm(FlaskForm):
    """
    User registration form.
    Validates username and email uniqueness.
    """
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64, message='Username must be between 3 and 64 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('I am a', choices=[
        ('client', 'Client (looking for services)'),
        ('provider', 'Service Provider')
    ], validators=[DataRequired()])
    location = StringField('Location', validators=[
        DataRequired(),
        Length(max=100)
    ])
    phone = StringField('Phone Number', validators=[
        Optional(),
        Length(max=20)
    ])
    
    def validate_username(self, username):
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class ProfileForm(FlaskForm):
    """User profile editing form"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address')
    ])
    location = StringField('Location', validators=[
        DataRequired(),
        Length(max=100)
    ])
    phone = StringField('Phone Number', validators=[
        Optional(),
        Length(max=20)
    ])
    bio = TextAreaField('Bio', validators=[
        Optional(),
        Length(max=500, message='Bio must not exceed 500 characters')
    ])


class ServiceForm(FlaskForm):
    """
    Service creation/editing form for providers.
    Includes validation for price and service details.
    """
    service_name = StringField('Service Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Service name must be between 3 and 100 characters')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, message='Please provide a detailed description (at least 10 characters)')
    ])
    category = SelectField('Category', choices=[
        ('cleaning', 'Cleaning'),
        ('handyman', 'Handyman'),
        ('tutoring', 'Tutoring'),
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('gardening', 'Gardening'),
        ('painting', 'Painting'),
        ('moving', 'Moving'),
        ('pet_care', 'Pet Care'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    price = FloatField('Price (per hour/session)', validators=[
        DataRequired(),
        NumberRange(min=0.01, message='Price must be greater than 0')
    ])


class AvailabilityForm(FlaskForm):
    """Form for adding availability slots"""
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    start_time = TimeField('Start Time', validators=[DataRequired()], format='%H:%M')
    end_time = TimeField('End Time', validators=[DataRequired()], format='%H:%M')
    
    def validate_end_time(self, end_time):
        """Ensure end time is after start time"""
        if self.start_time.data and end_time.data:
            if end_time.data <= self.start_time.data:
                raise ValidationError('End time must be after start time')


class BookingForm(FlaskForm):
    """Form for creating a booking"""
    notes = TextAreaField('Additional Notes', validators=[
        Optional(),
        Length(max=500)
    ])


class ReviewForm(FlaskForm):
    """
    Review submission form.
    Rating is required, comment is optional.
    """
    rating = SelectField('Rating', choices=[
        ('5', '5 - Excellent'),
        ('4', '4 - Good'),
        ('3', '3 - Average'),
        ('2', '2 - Below Average'),
        ('1', '1 - Poor')
    ], validators=[DataRequired()], coerce=int)
    comment = TextAreaField('Review', validators=[
        Optional(),
        Length(max=1000, message='Review must not exceed 1000 characters')
    ])


class SearchForm(FlaskForm):
    """Form for searching services"""
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('cleaning', 'Cleaning'),
        ('handyman', 'Handyman'),
        ('tutoring', 'Tutoring'),
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('gardening', 'Gardening'),
        ('painting', 'Painting'),
        ('moving', 'Moving'),
        ('pet_care', 'Pet Care'),
        ('other', 'Other')
    ])
    location = StringField('Location', validators=[Optional()])
    min_price = FloatField('Min Price', validators=[
        Optional(),
        NumberRange(min=0)
    ])
    max_price = FloatField('Max Price', validators=[
        Optional(),
        NumberRange(min=0)
    ])
    
    def validate_max_price(self, max_price):
        """Ensure max price is greater than min price"""
        if self.min_price.data and max_price.data:
            if max_price.data < self.min_price.data:
                raise ValidationError('Max price must be greater than min price')
