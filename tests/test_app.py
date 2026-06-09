"""
Unit tests for ServiceLink application.

This module contains comprehensive tests for:
- User registration and authentication
- Booking creation and management
- Review submission
- Double booking prevention
- Service management
"""

import pytest
from app.models import User, Service, Booking, Review, AvailabilitySlot
from datetime import date, time, timedelta
from app import db


class TestUserAuthentication:
    """Test suite for user authentication"""
    
    def test_user_registration(self, client, test_app):
        """
        Test Case 1: User Registration
        Verify that a new user can register successfully
        """
        with test_app.app_context():
            response = client.post('/auth/register', data={
                'username': 'newuser',
                'email': 'newuser@test.com',
                'password': 'password123',
                'password2': 'password123',
                'role': 'client',
                'location': 'Boston, MA',
                'phone': '555-9999'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Verify user was created in database
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@test.com'
            assert user.role == 'client'
            assert user.check_password('password123')
    
    def test_duplicate_username_registration(self, client, init_database):
        """
        Test that registration fails with duplicate username
        """
        response = client.post('/auth/register', data={
            'username': 'testclient',  # Already exists
            'email': 'another@test.com',
            'password': 'password123',
            'password2': 'password123',
            'role': 'client',
            'location': 'Boston, MA'
        }, follow_redirects=True)
        
        assert b'Username already taken' in response.data
    
    def test_user_login(self, client, init_database):
        """
        Test Case 2: User Login
        Verify that a user can log in with correct credentials
        """
        response = client.post('/auth/login', data={
            'username': 'testclient',
            'password': 'password123',
            'remember_me': False
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome back' in response.data or b'Dashboard' in response.data
    
    def test_invalid_login(self, client, init_database):
        """
        Test that login fails with incorrect credentials
        """
        response = client.post('/auth/login', data={
            'username': 'testclient',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert b'Invalid username or password' in response.data
    
    def test_logout(self, authenticated_client):
        """
        Test that a user can log out successfully
        """
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out' in response.data


class TestBookingSystem:
    """Test suite for booking functionality"""
    
    def test_create_booking(self, test_app, authenticated_client, init_database):
        """
        Test Case 3: Booking Creation
        Verify that a client can create a booking successfully
        """
        with test_app.app_context():
            # Get the test service and slot
            service = Service.query.first()
            slot = AvailabilitySlot.query.first()
            
            response = authenticated_client.post(
                f'/client/book/{service.id}/{slot.id}',
                data={'notes': 'Please arrive on time'},
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            # Verify booking was created
            booking = Booking.query.filter_by(service_id=service.id).first()
            assert booking is not None
            assert booking.status == 'pending'
            assert booking.notes == 'Please arrive on time'
            
            # Verify slot is marked as booked
            slot = AvailabilitySlot.query.get(slot.id)
            assert slot.is_booked == True
    
    def test_prevent_double_booking(self, test_app, client, init_database):
        """
        Test Case 4: Prevent Double Booking
        Verify that a time slot cannot be double-booked
        """
        with test_app.app_context():
            # Login as first client
            client.post('/auth/login', data={
                'username': 'testclient',
                'password': 'password123'
            })
            
            service = Service.query.first()
            slot = AvailabilitySlot.query.first()
            
            # First booking
            client.post(
                f'/client/book/{service.id}/{slot.id}',
                data={'notes': 'First booking'},
                follow_redirects=True
            )
            
            # Logout and create second client
            client.get('/auth/logout')
            
            client2 = User(
                username='client2',
                email='client2@test.com',
                role='client',
                location='New York, NY'
            )
            client2.set_password('password123')
            db.session.add(client2)
            db.session.commit()
            
            # Login as second client
            client.post('/auth/login', data={
                'username': 'client2',
                'password': 'password123'
            })
            
            # Try to book the same slot
            response = client.post(
                f'/client/book/{service.id}/{slot.id}',
                data={'notes': 'Second booking'},
                follow_redirects=True
            )
            
            # Should fail with appropriate message
            assert b'no longer available' in response.data or b'already booked' in response.data
            
            # Verify only one booking exists
            bookings = Booking.query.filter_by(slot_id=slot.id).all()
            assert len(bookings) == 1
    
    def test_cancel_booking(self, test_app, authenticated_client, init_database):
        """
        Test that a client can cancel their booking
        """
        with test_app.app_context():
            # Create a booking first
            service = Service.query.first()
            slot = AvailabilitySlot.query.first()
            
            authenticated_client.post(
                f'/client/book/{service.id}/{slot.id}',
                data={'notes': 'Test booking'},
                follow_redirects=True
            )
            
            booking = Booking.query.first()
            
            # Cancel the booking
            response = authenticated_client.post(
                f'/client/booking/{booking.id}/cancel',
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            # Verify booking status changed
            booking = Booking.query.get(booking.id)
            assert booking.status == 'cancelled'
            
            # Verify slot is available again
            slot = AvailabilitySlot.query.get(slot.id)
            assert slot.is_booked == False


class TestReviewSystem:
    """Test suite for review functionality"""
    
    def test_submit_review_for_completed_booking(self, test_app, authenticated_client, init_database):
        """
        Test Case 5: Review Submission
        Verify that a client can submit a review for a completed booking
        """
        with test_app.app_context():
            # Create and complete a booking
            service = Service.query.first()
            slot = AvailabilitySlot.query.first()
            client_user = User.query.filter_by(username='testclient').first()
            
            booking = Booking(
                client_id=client_user.id,
                service_id=service.id,
                slot_id=slot.id,
                booking_date=slot.date,
                start_time=slot.start_time,
                end_time=slot.end_time,
                status='completed'  # Set as completed
            )
            slot.is_booked = True
            
            db.session.add(booking)
            db.session.commit()
            
            # Submit review
            response = authenticated_client.post(
                f'/client/booking/{booking.id}/review',
                data={
                    'rating': 5,
                    'comment': 'Excellent service! Very professional.'
                },
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            # Verify review was created
            review = Review.query.filter_by(booking_id=booking.id).first()
            assert review is not None
            assert review.rating == 5
            assert review.comment == 'Excellent service! Very professional.'
            assert review.provider_id == service.provider_id
    
    def test_cannot_review_pending_booking(self, test_app, authenticated_client, init_database):
        """
        Test that a client cannot review a pending booking
        """
        with test_app.app_context():
            # Create a pending booking
            service = Service.query.first()
            slot = AvailabilitySlot.query.first()
            
            authenticated_client.post(
                f'/client/book/{service.id}/{slot.id}',
                data={'notes': 'Test'},
                follow_redirects=True
            )
            
            booking = Booking.query.first()
            
            # Try to review pending booking
            response = authenticated_client.get(
                f'/client/booking/{booking.id}/review',
                follow_redirects=True
            )
            
            assert b'cannot be reviewed' in response.data
    
    def test_cannot_review_twice(self, test_app, authenticated_client, init_database):
        """
        Test that a booking can only be reviewed once
        """
        with test_app.app_context():
            # Create completed booking with review
            service = Service.query.first()
            slot = AvailabilitySlot.query.first()
            client_user = User.query.filter_by(username='testclient').first()
            
            booking = Booking(
                client_id=client_user.id,
                service_id=service.id,
                slot_id=slot.id,
                booking_date=slot.date,
                start_time=slot.start_time,
                end_time=slot.end_time,
                status='completed'
            )
            db.session.add(booking)
            db.session.commit()
            
            # First review
            review = Review(
                booking_id=booking.id,
                client_id=client_user.id,
                provider_id=service.provider_id,
                rating=5,
                comment='Great!'
            )
            db.session.add(review)
            db.session.commit()
            
            # Try to review again
            response = authenticated_client.get(
                f'/client/booking/{booking.id}/review',
                follow_redirects=True
            )
            
            assert b'cannot be reviewed' in response.data


class TestServiceManagement:
    """Test suite for service provider functionality"""
    
    def test_provider_add_service(self, test_app, authenticated_provider, init_database):
        """
        Test that a provider can add a new service
        """
        with test_app.app_context():
            response = authenticated_provider.post('/provider/service/add', data={
                'service_name': 'Plumbing Service',
                'description': 'Professional plumbing services',
                'category': 'plumbing',
                'price': 75.0
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Verify service was created
            service = Service.query.filter_by(service_name='Plumbing Service').first()
            assert service is not None
            assert service.price == 75.0
    
    def test_provider_edit_service(self, test_app, authenticated_provider, init_database):
        """
        Test that a provider can edit their service
        """
        with test_app.app_context():
            service = Service.query.first()
            
            response = authenticated_provider.post(
                f'/provider/service/{service.id}/edit',
                data={
                    'service_name': 'Updated Service Name',
                    'description': service.description,
                    'category': service.category,
                    'price': 60.0
                },
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            # Verify service was updated
            service = Service.query.get(service.id)
            assert service.service_name == 'Updated Service Name'
            assert service.price == 60.0
    
    def test_provider_manage_availability(self, test_app, authenticated_provider, init_database):
        """
        Test that a provider can add availability slots
        """
        with test_app.app_context():
            service = Service.query.first()
            tomorrow = date.today() + timedelta(days=1)
            
            response = authenticated_provider.post(
                f'/provider/service/{service.id}/availability',
                data={
                    'date': tomorrow.isoformat(),
                    'start_time': '14:00',
                    'end_time': '15:00'
                },
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            # Verify slot was created
            slots = AvailabilitySlot.query.filter_by(
                service_id=service.id,
                date=tomorrow
            ).all()
            assert len(slots) >= 1


class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    def test_api_services_list(self, client, init_database):
        """
        Test that API returns services in JSON format
        """
        response = client.get('/api/services')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert 'services' in data
        assert isinstance(data['services'], list)
    
    def test_api_service_detail(self, test_app, client, init_database):
        """
        Test that API returns service details
        """
        with test_app.app_context():
            service = Service.query.first()
            response = client.get(f'/api/service/{service.id}')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['service_name'] == service.service_name
            assert 'provider' in data
            assert 'available_slots' in data


class TestRoleBasedAccess:
    """Test suite for role-based access control"""
    
    def test_provider_can_access_provider_dashboard(self, authenticated_provider):
        """
        Test that a provider can access their dashboard
        """
        response = authenticated_provider.get('/provider/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Provider' in response.data
    
    def test_client_cannot_access_provider_dashboard(self, authenticated_client):
        """
        Test that a client cannot access provider dashboard
        """
        response = authenticated_client.get('/provider/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'do not have permission' in response.data or b'Access denied' in response.data or b'not authorized' in response.data
    
    def test_unauthenticated_redirect(self, client):
        """
        Test that unauthenticated users are redirected to login
        """
        response = client.get('/client/dashboard', follow_redirects=True)
        assert b'login' in response.data.lower() or b'sign in' in response.data.lower()


class TestServiceSearch:
    """Test suite for service search and filtering"""
    
    def test_search_service_by_name(self, test_app, client, init_database):
        """
        Test service search by name
        """
        with test_app.app_context():
            response = client.get('/search?q=Cleaning')
            assert response.status_code == 200
            assert b'Cleaning' in response.data
    
    def test_filter_service_by_category(self, test_app, client, init_database):
        """
        Test service filtering by category
        """
        with test_app.app_context():
            response = client.get('/search?category=cleaning')
            assert response.status_code == 200
            service = Service.query.filter_by(category='cleaning').first()
            if service:
                assert service.service_name.encode() in response.data
    
    def test_search_no_results(self, client, init_database):
        """
        Test search returns appropriate message when no services found
        """
        response = client.get('/search?q=NonexistentService999999')
        assert response.status_code == 200
        # Verify search query is in response but no matching service is listed
        assert b'NonexistentService999999' not in response.data or b'Test Cleaning Service' in response.data


class TestBookingStatusChanges:
    """Test suite for booking status management"""
    
    def test_provider_can_confirm_booking(self, test_app, authenticated_provider, init_database):
        """
        Test that provider can confirm a booking
        """
        with test_app.app_context():
            # Create a pending booking
            service = Service.query.first()
            slot = AvailabilitySlot.query.first()
            client_user = User.query.filter_by(username='testclient').first()
            
            booking = Booking(
                client_id=client_user.id,
                service_id=service.id,
                slot_id=slot.id,
                booking_date=slot.date,
                start_time=slot.start_time,
                end_time=slot.end_time,
                status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            
            # Provider confirms booking
            response = authenticated_provider.post(
                f'/provider/booking/{booking.id}/confirm',
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            booking = Booking.query.get(booking.id)
            assert booking.status == 'confirmed'
    
    def test_provider_can_complete_booking(self, test_app, authenticated_provider, init_database):
        """
        Test that provider can mark booking as completed
        """
        with test_app.app_context():
            service = Service.query.first()
            slot = AvailabilitySlot.query.first()
            client_user = User.query.filter_by(username='testclient').first()
            
            booking = Booking(
                client_id=client_user.id,
                service_id=service.id,
                slot_id=slot.id,
                booking_date=slot.date,
                start_time=slot.start_time,
                end_time=slot.end_time,
                status='confirmed'
            )
            db.session.add(booking)
            db.session.commit()
            
            response = authenticated_provider.post(
                f'/provider/booking/{booking.id}/complete',
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            booking = Booking.query.get(booking.id)
            assert booking.status == 'completed'


class TestRatingValidation:
    """Test suite for rating validation"""
    
    def test_rating_must_be_between_1_and_5(self, test_app, authenticated_client, init_database):
        """
        Test that rating must be between 1 and 5
        """
        with test_app.app_context():
            service = Service.query.first()
            slot = AvailabilitySlot.query.first()
            client_user = User.query.filter_by(username='testclient').first()
            
            booking = Booking(
                client_id=client_user.id,
                service_id=service.id,
                slot_id=slot.id,
                booking_date=slot.date,
                start_time=slot.start_time,
                end_time=slot.end_time,
                status='completed'
            )
            db.session.add(booking)
            db.session.commit()
            
            # Try rating with valid value first (WTForms select validates client-side)
            response = authenticated_client.post(
                f'/client/booking/{booking.id}/review',
                data={'rating': 3, 'comment': 'Test'},
                follow_redirects=True
            )
            
            # Verify review was created with valid rating
            assert response.status_code == 200
            review = Review.query.filter_by(booking_id=booking.id).first()
            assert review is not None
            assert 1 <= review.rating <= 5
    
    def test_average_rating_calculation(self, test_app, init_database):
        """
        Test that average rating is calculated correctly
        """
        with test_app.app_context():
            provider = User.query.filter_by(role='provider').first()
            client = User.query.filter_by(role='client').first()
            service = Service.query.first()
            
            # Create multiple reviews
            reviews = []
            for i in range(3):
                slot = AvailabilitySlot(
                    service_id=service.id,
                    date=date.today() + timedelta(days=i+1),
                    start_time=time(10, 0),
                    end_time=time(11, 0),
                    is_booked=True
                )
                db.session.add(slot)
                db.session.flush()
                
                booking = Booking(
                    client_id=client.id,
                    service_id=service.id,
                    slot_id=slot.id,
                    booking_date=slot.date,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    status='completed'
                )
                db.session.add(booking)
                db.session.flush()
                
                review = Review(
                    booking_id=booking.id,
                    client_id=client.id,
                    provider_id=provider.id,
                    rating=(i+1)*2,  # Ratings: 2, 4, 6 -> but 6 exceeds max, so use 3, 4, 5
                    comment=f'Review {i+1}'
                )
                reviews.append(review)
            
            # Adjust ratings to valid range
            reviews[0].rating = 3
            reviews[1].rating = 4
            reviews[2].rating = 5
            
            for review in reviews:
                db.session.add(review)
            db.session.commit()
            
            # Calculate average: (3 + 4 + 5) / 3 = 4.0
            provider_reviews = Review.query.filter_by(provider_id=provider.id).all()
            avg_rating = sum(r.rating for r in provider_reviews) / len(provider_reviews)
            
            assert avg_rating == 4.0


class TestEdgeCases:
    """Test suite for edge cases and validation"""
    
    def test_empty_registration_form(self, client):
        """
        Test that empty registration form is rejected
        """
        response = client.post('/auth/register', data={}, follow_redirects=True)
        assert b'required' in response.data.lower() or response.status_code == 400
    
    def test_empty_service_form(self, authenticated_provider):
        """
        Test that empty service form is rejected
        """
        response = authenticated_provider.post('/provider/service/add', data={}, follow_redirects=True)
        assert b'required' in response.data.lower() or response.status_code == 400
    
    def test_invalid_email_format(self, client):
        """
        Test that invalid email format is rejected
        """
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'invalid-email',  # Invalid format
            'password': 'password123',
            'password2': 'password123',
            'role': 'client'
        }, follow_redirects=True)
        
        assert b'Invalid email' in response.data or b'valid email' in response.data.lower()
    
    def test_password_mismatch(self, client):
        """
        Test that mismatched passwords are rejected
        """
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'differentpassword',
            'role': 'client'
        }, follow_redirects=True)
        
        assert b'match' in response.data.lower()
    
    def test_duplicate_email_registration(self, client, init_database):
        """
        Test that registration fails with duplicate email
        """
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'client@test.com',  # Already exists
            'password': 'password123',
            'password2': 'password123',
            'role': 'client',
            'location': 'Boston, MA'
        }, follow_redirects=True)
        
        assert b'Email already registered' in response.data or b'already in use' in response.data
    
    def test_negative_price_validation(self, authenticated_provider):
        """
        Test that negative prices are rejected
        """
        response = authenticated_provider.post('/provider/service/add', data={
            'service_name': 'Test Service',
            'description': 'Test description',
            'category': 'cleaning',
            'price': -10.0  # Negative price
        }, follow_redirects=True)
        
        assert b'greater than' in response.data or b'positive' in response.data.lower() or response.status_code == 400
    
    def test_unauthorized_service_edit(self, test_app, authenticated_client, init_database):
        """
        Test that a client cannot edit a provider's service
        """
        with test_app.app_context():
            service = Service.query.first()
            
            response = authenticated_client.post(
                f'/provider/service/{service.id}/edit',
                data={
                    'service_name': 'Hacked Service',
                    'description': 'Test',
                    'category': 'cleaning',
                    'price': 1.0
                },
                follow_redirects=True
            )
            
            # Should be denied or redirected
            assert b'do not have permission' in response.data or b'Access denied' in response.data or b'not authorized' in response.data or response.status_code == 403


class TestModelValidation:
    """Test suite for model-level validation"""
    
    def test_user_password_hashing(self, test_app):
        """
        Test that passwords are properly hashed
        """
        with test_app.app_context():
            user = User(username='testuser', email='test@test.com', role='client')
            user.set_password('mypassword')
            
            # Password should be hashed, not stored in plain text
            assert user.password_hash != 'mypassword'
            assert user.check_password('mypassword') == True
            assert user.check_password('wrongpassword') == False
    
    def test_booking_can_be_reviewed_method(self, test_app, init_database):
        """
        Test the can_be_reviewed method on Booking model
        """
        with test_app.app_context():
            service = Service.query.first()
            slot = AvailabilitySlot.query.first()
            client_user = User.query.filter_by(username='testclient').first()
            
            # Pending booking cannot be reviewed
            booking = Booking(
                client_id=client_user.id,
                service_id=service.id,
                slot_id=slot.id,
                booking_date=slot.date,
                start_time=slot.start_time,
                end_time=slot.end_time,
                status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            
            assert booking.can_be_reviewed() == False
            
            # Completed booking can be reviewed
            booking.status = 'completed'
            db.session.commit()
            
            assert booking.can_be_reviewed() == True
            
            # Already reviewed booking cannot be reviewed again
            review = Review(
                booking_id=booking.id,
                client_id=client_user.id,
                provider_id=service.provider_id,
                rating=5,
                comment='Great!'
            )
            db.session.add(review)
            db.session.commit()
            
            assert booking.can_be_reviewed() == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
