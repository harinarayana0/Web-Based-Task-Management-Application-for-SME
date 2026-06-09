"""
Script to add sample bookings for a specific user.
"""
from app import create_app, db
from app.models import User, Service, Booking, AvailabilitySlot, Review
from datetime import date, time, timedelta
import random

app = create_app('development')

with app.app_context():
    # Get or create the janesmith user
    user = User.query.filter_by(username='janesmith').first()
    
    if not user:
        print("User 'janesmith' not found. Creating new user...")
        user = User(
            username='janesmith',
            email='janesmith@example.com',
            role='client',
            location='New York, NY',
            phone='555-1234'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print("Created user 'janesmith'")
    
    print(f"Adding bookings for user: {user.username}")
    
    # Get all services
    services = Service.query.all()
    
    if not services:
        print("No services found! Please run 'flask seed-db' first.")
        exit(1)
    
    # Clear existing bookings for this user
    existing_bookings = Booking.query.filter_by(client_id=user.id).all()
    for booking in existing_bookings:
        db.session.delete(booking)
    db.session.commit()
    
    # Create 3 completed bookings (past dates)
    print("Creating completed bookings...")
    completed_count = 0
    for i in range(3):
        service = random.choice(services)
        past_date = date.today() - timedelta(days=random.randint(7, 30))
        
        # Create a slot for this booking
        slot = AvailabilitySlot(
            service_id=service.id,
            date=past_date,
            start_time=time(10, 0),
            end_time=time(11, 0),
            is_booked=True
        )
        db.session.add(slot)
        db.session.flush()
        
        # Create the booking
        booking = Booking(
            client_id=user.id,
            service_id=service.id,
            slot_id=slot.id,
            booking_date=past_date,
            start_time=time(10, 0),
            end_time=time(11, 0),
            status='completed',
            notes=f'Great service #{i+1}'
        )
        db.session.add(booking)
        db.session.flush()
        
        # Add a review for the completed booking
        review = Review(
            booking_id=booking.id,
            client_id=user.id,
            provider_id=service.provider_id,
            rating=random.randint(4, 5),
            comment=f'Excellent service! Very professional and thorough.'
        )
        db.session.add(review)
        completed_count += 1
    
    # Create 2 confirmed bookings (upcoming)
    print("Creating confirmed bookings...")
    confirmed_count = 0
    for i in range(2):
        service = random.choice(services)
        future_date = date.today() + timedelta(days=random.randint(3, 10))
        
        # Find or create an available slot
        slot = AvailabilitySlot.query.filter_by(
            service_id=service.id,
            date=future_date,
            is_booked=False
        ).first()
        
        if not slot:
            slot = AvailabilitySlot(
                service_id=service.id,
                date=future_date,
                start_time=time(14, 0),
                end_time=time(15, 0),
                is_booked=True
            )
            db.session.add(slot)
            db.session.flush()
        else:
            slot.is_booked = True
        
        booking = Booking(
            client_id=user.id,
            service_id=service.id,
            slot_id=slot.id,
            booking_date=future_date,
            start_time=slot.start_time,
            end_time=slot.end_time,
            status='confirmed',
            notes=f'Looking forward to this service'
        )
        db.session.add(booking)
        confirmed_count += 1
    
    # Create 2 pending bookings (very recent)
    print("Creating pending bookings...")
    pending_count = 0
    for i in range(2):
        service = random.choice(services)
        future_date = date.today() + timedelta(days=random.randint(1, 5))
        
        # Find or create an available slot
        slot = AvailabilitySlot.query.filter_by(
            service_id=service.id,
            date=future_date,
            is_booked=False
        ).first()
        
        if not slot:
            slot = AvailabilitySlot(
                service_id=service.id,
                date=future_date,
                start_time=time(16, 0),
                end_time=time(17, 0),
                is_booked=True
            )
            db.session.add(slot)
            db.session.flush()
        else:
            slot.is_booked = True
        
        booking = Booking(
            client_id=user.id,
            service_id=service.id,
            slot_id=slot.id,
            booking_date=future_date,
            start_time=slot.start_time,
            end_time=slot.end_time,
            status='pending',
            notes='Please confirm at your earliest convenience'
        )
        db.session.add(booking)
        pending_count += 1
    
    db.session.commit()
    
    print("\n" + "="*50)
    print("Bookings successfully created!")
    print("="*50)
    print(f"Completed bookings: {completed_count}")
    print(f"Confirmed bookings: {confirmed_count}")
    print(f"Pending bookings: {pending_count}")
    print(f"Total bookings: {completed_count + confirmed_count + pending_count}")
    print("\nRefresh your dashboard to see the bookings!")
    print("="*50)
