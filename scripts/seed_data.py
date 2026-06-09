"""
Database seed script for ServiceLink application.

This script populates the database with sample data for development and testing.
Includes sample users, services, bookings, and reviews.
"""

from app import create_app, db
from app.models import User, Service, Booking, Review, AvailabilitySlot
from datetime import date, time, timedelta
import random


def seed_database():
    """
    Seed the database with sample data.
    """
    app = create_app('development')
    
    with app.app_context():
        print("Starting database seeding...")
        
        # Clear existing data
        print("Clearing existing data...")
        db.session.query(Review).delete()
        db.session.query(Booking).delete()
        db.session.query(AvailabilitySlot).delete()
        db.session.query(Service).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        # Create clients
        print("Creating clients...")
        clients = []
        client_data = [
            ('john_doe', 'john@example.com', 'New York, NY', '555-0101'),
            ('jane_smith', 'jane@example.com', 'Brooklyn, NY', '555-0102'),
            ('mike_wilson', 'mike@example.com', 'Queens, NY', '555-0103'),
            ('sarah_jones', 'sarah@example.com', 'Manhattan, NY', '555-0104'),
            ('david_brown', 'david@example.com', 'Bronx, NY', '555-0105'),
        ]
        
        for username, email, location, phone in client_data:
            client = User(
                username=username,
                email=email,
                role='client',
                location=location,
                phone=phone
            )
            client.set_password('password123')
            clients.append(client)
            db.session.add(client)
        
        # Create providers
        print("Creating service providers...")
        providers = []
        provider_data = [
            ('clean_pro', 'cleanpro@example.com', 'New York, NY', '555-0201',
             'Professional cleaning service with 10+ years of experience'),
            ('handy_helper', 'handy@example.com', 'Brooklyn, NY', '555-0202',
             'Expert handyman for all your home repair needs'),
            ('tutor_ace', 'tutor@example.com', 'Manhattan, NY', '555-0203',
             'Experienced tutor specializing in math and science'),
            ('plumb_expert', 'plumber@example.com', 'Queens, NY', '555-0204',
             'Licensed plumber with 15 years of experience'),
            ('electric_pro', 'electric@example.com', 'Bronx, NY', '555-0205',
             'Certified electrician for residential and commercial work'),
            ('green_thumb', 'garden@example.com', 'Staten Island, NY', '555-0206',
             'Professional gardening and landscaping services'),
            ('paint_master', 'painter@example.com', 'New York, NY', '555-0207',
             'Quality painting services for interior and exterior'),
            ('move_easy', 'mover@example.com', 'Brooklyn, NY', '555-0208',
             'Reliable moving service for local and long-distance moves'),
        ]
        
        for username, email, location, phone, bio in provider_data:
            provider = User(
                username=username,
                email=email,
                role='provider',
                location=location,
                phone=phone,
                bio=bio
            )
            provider.set_password('password123')
            providers.append(provider)
            db.session.add(provider)
        
        db.session.commit()
        print(f"Created {len(clients)} clients and {len(providers)} providers")
        
        # Create services
        print("Creating services...")
        services = []
        service_data = [
            (providers[0].id, 'House Cleaning', 'Deep cleaning for your entire home', 'cleaning', 45.0),
            (providers[0].id, 'Office Cleaning', 'Professional office cleaning services', 'cleaning', 55.0),
            (providers[1].id, 'Home Repair', 'General home repairs and maintenance', 'handyman', 60.0),
            (providers[1].id, 'Furniture Assembly', 'Expert furniture assembly service', 'handyman', 40.0),
            (providers[2].id, 'Math Tutoring', 'High school and college math tutoring', 'tutoring', 50.0),
            (providers[2].id, 'Science Tutoring', 'Physics, Chemistry, and Biology tutoring', 'tutoring', 50.0),
            (providers[3].id, 'Plumbing Repair', 'Emergency and scheduled plumbing repairs', 'plumbing', 75.0),
            (providers[3].id, 'Drain Cleaning', 'Professional drain cleaning and unclogging', 'plumbing', 65.0),
            (providers[4].id, 'Electrical Repair', 'Licensed electrical repairs and installations', 'electrical', 80.0),
            (providers[4].id, 'Lighting Installation', 'Install new lighting fixtures', 'electrical', 70.0),
            (providers[5].id, 'Lawn Maintenance', 'Regular lawn mowing and maintenance', 'gardening', 40.0),
            (providers[5].id, 'Garden Design', 'Professional garden design and planting', 'gardening', 60.0),
            (providers[6].id, 'Interior Painting', 'Quality interior painting services', 'painting', 50.0),
            (providers[6].id, 'Exterior Painting', 'Weather-resistant exterior painting', 'painting', 55.0),
            (providers[7].id, 'Local Moving', 'Local moving services with care', 'moving', 90.0),
            (providers[7].id, 'Packing Service', 'Professional packing for your move', 'moving', 45.0),
        ]
        
        for provider_id, name, desc, category, price in service_data:
            service = Service(
                provider_id=provider_id,
                service_name=name,
                description=desc,
                category=category,
                price=price
            )
            services.append(service)
            db.session.add(service)
        
        db.session.commit()
        print(f"Created {len(services)} services")
        
        # Create availability slots
        print("Creating availability slots...")
        slots = []
        start_date = date.today()
        
        for service in services:
            # Create slots for next 14 days
            for day in range(14):
                slot_date = start_date + timedelta(days=day)
                # Create 4 slots per day
                time_slots = [
                    (time(9, 0), time(10, 0)),
                    (time(11, 0), time(12, 0)),
                    (time(14, 0), time(15, 0)),
                    (time(16, 0), time(17, 0)),
                ]
                
                for start_time, end_time in time_slots:
                    slot = AvailabilitySlot(
                        service_id=service.id,
                        date=slot_date,
                        start_time=start_time,
                        end_time=end_time,
                        is_booked=False
                    )
                    slots.append(slot)
                    db.session.add(slot)
        
        db.session.commit()
        print(f"Created {len(slots)} availability slots")
        
        # Create some bookings
        print("Creating sample bookings...")
        bookings = []
        
        # Create past bookings (completed)
        for i in range(10):
            client = random.choice(clients)
            service = random.choice(services)
            slot_date = start_date - timedelta(days=random.randint(1, 30))
            
            slot = AvailabilitySlot(
                service_id=service.id,
                date=slot_date,
                start_time=time(10, 0),
                end_time=time(11, 0),
                is_booked=True
            )
            db.session.add(slot)
            db.session.commit()
            
            booking = Booking(
                client_id=client.id,
                service_id=service.id,
                slot_id=slot.id,
                booking_date=slot_date,
                start_time=time(10, 0),
                end_time=time(11, 0),
                status='completed',
                notes='Sample booking'
            )
            bookings.append(booking)
            db.session.add(booking)
        
        # Create some pending bookings
        for i in range(5):
            client = random.choice(clients)
            service = random.choice(services)
            available_slot = AvailabilitySlot.query.filter_by(
                service_id=service.id,
                is_booked=False
            ).first()
            
            if available_slot:
                available_slot.is_booked = True
                booking = Booking(
                    client_id=client.id,
                    service_id=service.id,
                    slot_id=available_slot.id,
                    booking_date=available_slot.date,
                    start_time=available_slot.start_time,
                    end_time=available_slot.end_time,
                    status='pending',
                    notes='Looking forward to the service'
                )
                bookings.append(booking)
                db.session.add(booking)
        
        db.session.commit()
        print(f"Created {len(bookings)} bookings")
        
        # Create reviews for completed bookings
        print("Creating reviews...")
        reviews = []
        completed_bookings = [b for b in bookings if b.status == 'completed']
        
        comments = [
            'Excellent service! Very professional and thorough.',
            'Great experience, will definitely book again.',
            'Good service, arrived on time and did a great job.',
            'Very satisfied with the quality of work.',
            'Professional and courteous. Highly recommend!',
            'Outstanding service! Exceeded my expectations.',
            'Reliable and efficient. Would use again.',
            'Good value for money. Quality work.',
            'Friendly and knowledgeable. Great service!',
            'Very pleased with the results. Thank you!',
        ]
        
        for booking in completed_bookings[:8]:  # Review 8 out of 10
            rating = random.randint(4, 5)  # Mostly good ratings
            comment = random.choice(comments)
            
            review = Review(
                booking_id=booking.id,
                client_id=booking.client_id,
                provider_id=booking.service.provider_id,
                rating=rating,
                comment=comment
            )
            reviews.append(review)
            db.session.add(review)
        
        db.session.commit()
        print(f"Created {len(reviews)} reviews")
        
        print("\n" + "="*50)
        print("Database seeding completed successfully!")
        print("="*50)
        print("\nSample credentials:")
        print("\nClients:")
        print("  Username: john_doe | Password: password123")
        print("  Username: jane_smith | Password: password123")
        print("\nProviders:")
        print("  Username: clean_pro | Password: password123")
        print("  Username: handy_helper | Password: password123")
        print("="*50)


if __name__ == '__main__':
    seed_database()
