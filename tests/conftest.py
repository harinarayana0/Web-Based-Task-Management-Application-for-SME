"""
Test configuration and fixtures for ServiceLink application.

This module provides pytest fixtures and configuration for testing.
"""

import pytest
from app import create_app, db
from app.models import User, Service, Booking, Review, AvailabilitySlot
from datetime import date, time, datetime, timedelta


@pytest.fixture(scope='module')
def test_app():
    """
    Create and configure a test application instance.
    Uses in-memory SQLite database for testing.
    """
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(test_app):
    """
    Provide a test client for the application.
    """
    return test_app.test_client()


@pytest.fixture(scope='function')
def init_database(test_app):
    """
    Initialize database with test data for each test function.
    """
    with test_app.app_context():
        # Create test users
        client_user = User(
            username='testclient',
            email='client@test.com',
            role='client',
            location='New York, NY',
            phone='555-1234'
        )
        client_user.set_password('password123')
        
        provider_user = User(
            username='testprovider',
            email='provider@test.com',
            role='provider',
            location='New York, NY',
            phone='555-5678',
            bio='Professional service provider'
        )
        provider_user.set_password('password123')
        
        db.session.add(client_user)
        db.session.add(provider_user)
        db.session.commit()
        
        # Create test service
        service = Service(
            provider_id=provider_user.id,
            service_name='Test Cleaning Service',
            description='Professional cleaning service for your home',
            category='cleaning',
            price=50.0
        )
        
        db.session.add(service)
        db.session.commit()
        
        # Create availability slot
        slot = AvailabilitySlot(
            service_id=service.id,
            date=date.today() + timedelta(days=1),
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_booked=False
        )
        
        db.session.add(slot)
        db.session.commit()
        
        yield db
        
        # Cleanup
        db.session.query(Review).delete()
        db.session.query(Booking).delete()
        db.session.query(AvailabilitySlot).delete()
        db.session.query(Service).delete()
        db.session.query(User).delete()
        db.session.commit()


@pytest.fixture
def authenticated_client(client, init_database):
    """
    Provide an authenticated client session.
    """
    # Login as client
    client.post('/auth/login', data={
        'username': 'testclient',
        'password': 'password123',
        'csrf_token': 'test'  # CSRF is disabled in testing config
    }, follow_redirects=True)
    
    return client


@pytest.fixture
def authenticated_provider(client, init_database):
    """
    Provide an authenticated provider session.
    """
    # Login as provider
    client.post('/auth/login', data={
        'username': 'testprovider',
        'password': 'password123',
        'csrf_token': 'test'
    }, follow_redirects=True)
    
    return client
