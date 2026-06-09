"""
Routes and view functions for ServiceLink application.

This module defines all the routes (endpoints) for the application.
Routes are organized into blueprints for better modularity:
- main: Public pages (home, about)
- auth: Authentication (register, login, logout)
- provider: Provider-specific functionality
- client: Client-specific functionality
- api: RESTful API endpoints

Design decisions:
- Blueprint pattern for modular organization
- Role-based access control using decorators
- Consistent error handling
- Proper input validation and sanitization
"""

from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, jsonify, abort)
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Service, Booking, Review, AvailabilitySlot
from app.forms import (RegistrationForm, LoginForm, ServiceForm, BookingForm,
                      ReviewForm, SearchForm, ProfileForm, AvailabilityForm)
from datetime import datetime, date, time
from functools import wraps
from sqlalchemy import or_, and_

# Define blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
provider_bp = Blueprint('provider', __name__)
client_bp = Blueprint('client', __name__)
api_bp = Blueprint('api', __name__)


# ============================================================================
# DECORATORS
# ============================================================================

def role_required(role):
    """
    Decorator to restrict access to specific user roles.
    
    Args:
        role (str): Required role ('client' or 'provider')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role != role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================================
# MAIN ROUTES (Public)
# ============================================================================

@main_bp.route('/')
def index():
    """Home page with featured services"""
    # Get recent services with high ratings
    services = Service.query.filter_by(is_active=True).order_by(
        Service.created_at.desc()
    ).limit(6).all()
    
    return render_template('index.html', services=services)


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@main_bp.route('/search')
def search():
    """
    Search and filter services.
    Supports filtering by category, location, and price range.
    """
    form = SearchForm(request.args, meta={'csrf': False})
    
    # Start with all active services
    query = Service.query.filter_by(is_active=True)
    
    # Apply filters
    if form.category.data:
        query = query.filter_by(category=form.category.data)
    
    if form.location.data:
        # Search in provider's location
        query = query.join(User).filter(
            User.location.ilike(f'%{form.location.data}%')
        )
    
    if form.min_price.data is not None:
        query = query.filter(Service.price >= form.min_price.data)
    
    if form.max_price.data is not None:
        query = query.filter(Service.price <= form.max_price.data)
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(
        page=page,
        per_page=9,
        error_out=False
    )
    
    return render_template('search.html',
                         form=form,
                         services=pagination.items,
                         pagination=pagination)


@main_bp.route('/service/<int:service_id>')
def service_detail(service_id):
    """
    Service detail page showing information and reviews.
    
    Args:
        service_id: ID of the service to display
    """
    service = Service.query.get_or_404(service_id)
    
    # Get reviews for this service's provider
    reviews = Review.query.filter_by(provider_id=service.provider_id).order_by(
        Review.created_at.desc()
    ).limit(10).all()
    
    # Get available slots
    available_slots = AvailabilitySlot.query.filter(
        AvailabilitySlot.service_id == service_id,
        AvailabilitySlot.is_booked == False,
        AvailabilitySlot.date >= date.today()
    ).order_by(AvailabilitySlot.date, AvailabilitySlot.start_time).all()
    
    return render_template('service_detail.html',
                         service=service,
                         reviews=reviews,
                         available_slots=available_slots)


@main_bp.route('/provider/<int:provider_id>')
def provider_profile(provider_id):
    """
    Public provider profile page.
    
    Args:
        provider_id: ID of the provider
    """
    provider = User.query.get_or_404(provider_id)
    
    if provider.role != 'provider':
        abort(404)
    
    services = Service.query.filter_by(provider_id=provider_id, is_active=True).all()
    reviews = Review.query.filter_by(provider_id=provider_id).order_by(
        Review.created_at.desc()
    ).limit(10).all()
    
    return render_template('provider_profile.html',
                         provider=provider,
                         services=services,
                         reviews=reviews)


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            location=form.location.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to appropriate dashboard based on role
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            if user.role == 'provider':
                next_page = url_for('provider.dashboard')
            else:
                next_page = url_for('client.dashboard')
        
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# ============================================================================
# PROVIDER ROUTES
# ============================================================================

@provider_bp.route('/dashboard')
@login_required
@role_required('provider')
def dashboard():
    """Provider dashboard showing services and bookings"""
    services = Service.query.filter_by(provider_id=current_user.id).all()
    
    # Get recent bookings for provider's services
    bookings = Booking.query.join(Service).filter(
        Service.provider_id == current_user.id
    ).order_by(Booking.created_at.desc()).limit(10).all()
    
    # Get statistics
    total_bookings = Booking.query.join(Service).filter(
        Service.provider_id == current_user.id
    ).count()
    
    completed_bookings = Booking.query.join(Service).filter(
        Service.provider_id == current_user.id,
        Booking.status == 'completed'
    ).count()
    
    pending_bookings = Booking.query.join(Service).filter(
        Service.provider_id == current_user.id,
        Booking.status == 'pending'
    ).count()
    
    return render_template('provider/dashboard.html',
                         services=services,
                         bookings=bookings,
                         total_bookings=total_bookings,
                         completed_bookings=completed_bookings,
                         pending_bookings=pending_bookings)


@provider_bp.route('/services')
@login_required
@role_required('provider')
def services():
    """List all services offered by the provider"""
    services = Service.query.filter_by(provider_id=current_user.id).all()
    return render_template('provider/services.html', services=services)


@provider_bp.route('/service/add', methods=['GET', 'POST'])
@login_required
@role_required('provider')
def add_service():
    """Add a new service"""
    form = ServiceForm()
    
    if form.validate_on_submit():
        service = Service(
            provider_id=current_user.id,
            service_name=form.service_name.data,
            description=form.description.data,
            category=form.category.data,
            price=form.price.data
        )
        
        db.session.add(service)
        db.session.commit()
        
        flash('Service added successfully!', 'success')
        return redirect(url_for('provider.services'))
    
    return render_template('provider/add_service.html', form=form)


@provider_bp.route('/service/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('provider')
def edit_service(service_id):
    """Edit an existing service"""
    service = Service.query.get_or_404(service_id)
    
    # Ensure the service belongs to the current user
    if service.provider_id != current_user.id:
        abort(403)
    
    form = ServiceForm(obj=service)
    
    if form.validate_on_submit():
        service.service_name = form.service_name.data
        service.description = form.description.data
        service.category = form.category.data
        service.price = form.price.data
        
        db.session.commit()
        
        flash('Service updated successfully!', 'success')
        return redirect(url_for('provider.services'))
    
    return render_template('provider/edit_service.html', form=form, service=service)


@provider_bp.route('/service/<int:service_id>/delete', methods=['POST'])
@login_required
@role_required('provider')
def delete_service(service_id):
    """Delete a service"""
    service = Service.query.get_or_404(service_id)
    
    # Ensure the service belongs to the current user
    if service.provider_id != current_user.id:
        abort(403)
    
    # Check if there are pending bookings
    pending_bookings = Booking.query.filter_by(
        service_id=service_id,
        status='pending'
    ).count()
    
    if pending_bookings > 0:
        flash('Cannot delete service with pending bookings. Please complete or cancel them first.', 'danger')
        return redirect(url_for('provider.services'))
    
    db.session.delete(service)
    db.session.commit()
    
    flash('Service deleted successfully!', 'success')
    return redirect(url_for('provider.services'))


@provider_bp.route('/service/<int:service_id>/availability', methods=['GET', 'POST'])
@login_required
@role_required('provider')
def manage_availability(service_id):
    """Manage availability slots for a service"""
    service = Service.query.get_or_404(service_id)
    
    # Ensure the service belongs to the current user
    if service.provider_id != current_user.id:
        abort(403)
    
    form = AvailabilityForm()
    
    if form.validate_on_submit():
        slot = AvailabilitySlot(
            service_id=service_id,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data
        )
        
        db.session.add(slot)
        db.session.commit()
        
        flash('Availability slot added successfully!', 'success')
        return redirect(url_for('provider.manage_availability', service_id=service_id))
    
    # Get existing slots
    slots = AvailabilitySlot.query.filter_by(service_id=service_id).order_by(
        AvailabilitySlot.date.desc(),
        AvailabilitySlot.start_time.desc()
    ).all()
    
    return render_template('provider/availability.html',
                         form=form,
                         service=service,
                         slots=slots)


@provider_bp.route('/availability/<int:slot_id>/delete', methods=['POST'])
@login_required
@role_required('provider')
def delete_availability(slot_id):
    """Delete an availability slot"""
    slot = AvailabilitySlot.query.get_or_404(slot_id)
    service = Service.query.get_or_404(slot.service_id)
    
    # Ensure the service belongs to the current user
    if service.provider_id != current_user.id:
        abort(403)
    
    # Check if slot is booked
    if slot.is_booked:
        flash('Cannot delete a booked slot!', 'danger')
        return redirect(url_for('provider.manage_availability', service_id=service.id))
    
    db.session.delete(slot)
    db.session.commit()
    
    flash('Availability slot deleted successfully!', 'success')
    return redirect(url_for('provider.manage_availability', service_id=service.id))


@provider_bp.route('/bookings')
@login_required
@role_required('provider')
def bookings():
    """View all bookings for provider's services"""
    page = request.args.get('page', 1, type=int)
    
    bookings = Booking.query.join(Service).filter(
        Service.provider_id == current_user.id
    ).order_by(Booking.booking_date.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    
    return render_template('provider/bookings.html', bookings=bookings)


@provider_bp.route('/booking/<int:booking_id>/confirm', methods=['POST'])
@login_required
@role_required('provider')
def confirm_booking(booking_id):
    """Confirm a pending booking"""
    booking = Booking.query.get_or_404(booking_id)
    service = Service.query.get_or_404(booking.service_id)
    
    # Ensure the service belongs to the current user
    if service.provider_id != current_user.id:
        abort(403)
    
    if booking.status != 'pending':
        flash('Only pending bookings can be confirmed.', 'warning')
        return redirect(url_for('provider.bookings'))
    
    booking.status = 'confirmed'
    db.session.commit()
    
    flash('Booking confirmed successfully!', 'success')
    return redirect(url_for('provider.bookings'))


@provider_bp.route('/booking/<int:booking_id>/complete', methods=['POST'])
@login_required
@role_required('provider')
def complete_booking(booking_id):
    """Mark a booking as completed"""
    booking = Booking.query.get_or_404(booking_id)
    service = Service.query.get_or_404(booking.service_id)
    
    # Ensure the service belongs to the current user
    if service.provider_id != current_user.id:
        abort(403)
    
    if booking.status not in ['pending', 'confirmed']:
        flash('Invalid booking status.', 'warning')
        return redirect(url_for('provider.bookings'))
    
    booking.status = 'completed'
    db.session.commit()
    
    flash('Booking marked as completed!', 'success')
    return redirect(url_for('provider.bookings'))


@provider_bp.route('/reviews')
@login_required
@role_required('provider')
def reviews():
    """View all reviews received"""
    reviews = Review.query.filter_by(provider_id=current_user.id).order_by(
        Review.created_at.desc()
    ).all()
    
    return render_template('provider/reviews.html', reviews=reviews)


@provider_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('provider')
def profile():
    """Edit provider profile"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.location = form.location.data
        current_user.phone = form.phone.data
        current_user.bio = form.bio.data
        
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('provider.profile'))
    
    return render_template('provider/profile.html', form=form)


# ============================================================================
# CLIENT ROUTES
# ============================================================================

@client_bp.route('/dashboard')
@login_required
@role_required('client')
def dashboard():
    """Client dashboard showing bookings and activity"""
    # Get recent bookings
    bookings = Booking.query.filter_by(client_id=current_user.id).order_by(
        Booking.created_at.desc()
    ).limit(10).all()
    
    # Get statistics
    total_bookings = Booking.query.filter_by(client_id=current_user.id).count()
    
    completed_bookings = Booking.query.filter_by(
        client_id=current_user.id,
        status='completed'
    ).count()
    
    pending_bookings = Booking.query.filter_by(
        client_id=current_user.id,
        status='pending'
    ).count()
    
    return render_template('client/dashboard.html',
                         bookings=bookings,
                         total_bookings=total_bookings,
                         completed_bookings=completed_bookings,
                         pending_bookings=pending_bookings)


@client_bp.route('/book/<int:service_id>/<int:slot_id>', methods=['GET', 'POST'])
@login_required
@role_required('client')
def book_service(service_id, slot_id):
    """
    Book a service.
    Prevents double booking by checking slot availability.
    """
    service = Service.query.get_or_404(service_id)
    slot = AvailabilitySlot.query.get_or_404(slot_id)
    
    # Validate slot belongs to service
    if slot.service_id != service_id:
        abort(400)
    
    # Check if slot is already booked
    if slot.is_booked:
        flash('This time slot is no longer available.', 'warning')
        return redirect(url_for('main.service_detail', service_id=service_id))
    
    form = BookingForm()
    
    if form.validate_on_submit():
        # Double-check slot availability before creating booking
        if slot.is_booked:
            flash('This time slot was just booked. Please select another slot.', 'warning')
            return redirect(url_for('main.service_detail', service_id=service_id))
        
        # Create booking
        booking = Booking(
            client_id=current_user.id,
            service_id=service_id,
            slot_id=slot_id,
            booking_date=slot.date,
            start_time=slot.start_time,
            end_time=slot.end_time,
            notes=form.notes.data
        )
        
        # Mark slot as booked
        slot.is_booked = True
        
        db.session.add(booking)
        db.session.commit()
        
        flash('Booking created successfully! The provider will confirm shortly.', 'success')
        return redirect(url_for('client.bookings'))
    
    return render_template('client/book_service.html',
                         form=form,
                         service=service,
                         slot=slot)


@client_bp.route('/bookings')
@login_required
@role_required('client')
def bookings():
    """View all client bookings"""
    page = request.args.get('page', 1, type=int)
    
    bookings = Booking.query.filter_by(client_id=current_user.id).order_by(
        Booking.booking_date.desc()
    ).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    
    return render_template('client/bookings.html', bookings=bookings)


@client_bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
@role_required('client')
def cancel_booking(booking_id):
    """Cancel a booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure the booking belongs to the current user
    if booking.client_id != current_user.id:
        abort(403)
    
    if booking.status in ['completed', 'cancelled']:
        flash('This booking cannot be cancelled.', 'warning')
        return redirect(url_for('client.bookings'))
    
    # Free up the slot
    slot = AvailabilitySlot.query.get(booking.slot_id)
    if slot:
        slot.is_booked = False
    
    booking.status = 'cancelled'
    db.session.commit()
    
    flash('Booking cancelled successfully!', 'success')
    return redirect(url_for('client.bookings'))


@client_bp.route('/booking/<int:booking_id>/review', methods=['GET', 'POST'])
@login_required
@role_required('client')
def review_booking(booking_id):
    """
    Submit a review for a completed booking.
    Only completed bookings can be reviewed, and only once.
    """
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure the booking belongs to the current user
    if booking.client_id != current_user.id:
        abort(403)
    
    # Check if booking can be reviewed
    if not booking.can_be_reviewed():
        flash('This booking cannot be reviewed.', 'warning')
        return redirect(url_for('client.bookings'))
    
    form = ReviewForm()
    
    if form.validate_on_submit():
        review = Review(
            booking_id=booking_id,
            client_id=current_user.id,
            provider_id=booking.service.provider_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('client.bookings'))
    
    return render_template('client/review.html',
                         form=form,
                         booking=booking)


@client_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('client')
def profile():
    """Edit client profile"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.location = form.location.data
        current_user.phone = form.phone.data
        current_user.bio = form.bio.data
        
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('client.profile'))
    
    return render_template('client/profile.html', form=form)


# ============================================================================
# API ROUTES (JSON endpoints)
# ============================================================================

@api_bp.route('/services')
def api_services():
    """
    API endpoint to get all services in JSON format.
    Supports filtering by category and location.
    
    Query parameters:
        category (str): Filter by category
        location (str): Filter by provider location
        page (int): Page number for pagination
    
    Returns:
        JSON response with services list
    """
    # Get query parameters
    category = request.args.get('category')
    location = request.args.get('location')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build query
    query = Service.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if location:
        query = query.join(User).filter(User.location.ilike(f'%{location}%'))
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Serialize services
    services_data = [{
        'id': service.id,
        'service_name': service.service_name,
        'description': service.description,
        'category': service.category,
        'price': service.price,
        'provider': {
            'id': service.provider.id,
            'username': service.provider.username,
            'location': service.provider.location
        },
        'average_rating': service.get_average_rating(),
        'created_at': service.created_at.isoformat()
    } for service in pagination.items]
    
    return jsonify({
        'services': services_data,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': per_page
    })


@api_bp.route('/service/<int:service_id>')
def api_service_detail(service_id):
    """
    API endpoint to get service details.
    
    Args:
        service_id: Service ID
    
    Returns:
        JSON response with service details
    """
    service = Service.query.get_or_404(service_id)
    
    # Get available slots
    available_slots = AvailabilitySlot.query.filter(
        AvailabilitySlot.service_id == service_id,
        AvailabilitySlot.is_booked == False,
        AvailabilitySlot.date >= date.today()
    ).order_by(AvailabilitySlot.date, AvailabilitySlot.start_time).all()
    
    # Serialize
    service_data = {
        'id': service.id,
        'service_name': service.service_name,
        'description': service.description,
        'category': service.category,
        'price': service.price,
        'provider': {
            'id': service.provider.id,
            'username': service.provider.username,
            'location': service.provider.location,
            'bio': service.provider.bio,
            'average_rating': service.provider.get_average_rating()
        },
        'average_rating': service.get_average_rating(),
        'created_at': service.created_at.isoformat(),
        'available_slots': [{
            'id': slot.id,
            'date': slot.date.isoformat(),
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M')
        } for slot in available_slots]
    }
    
    return jsonify(service_data)
