"""
CSR Super Admin Blueprint
Network-wide administration for CSR Super Admins only
"""

from functools import wraps
from datetime import datetime, date, time
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Library, Seat, SystemSettings, Booking, User, LibraryAdmin, AdminRole, SeatCategory, BookingStatus, GalleryImage, GalleryStatus
from services.analytics import AnalyticsService

csr_admin_bp = Blueprint('csr_admin', __name__, url_prefix='/csr-admin')

def csr_super_admin_required(f):
    """Decorator to ensure user is CSR Super Admin"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_csr_super_admin:
            flash('You must be a CSR Super Admin to access this page', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@csr_admin_bp.route('/')
@csr_super_admin_required
def dashboard():
    """CSR Super Admin dashboard with network-wide analytics"""
    # Get network summary
    summary = AnalyticsService.get_network_summary()
    
    # Get library utilization data
    utilization_raw = AnalyticsService.get_library_utilization(days=30)
    
    # Enhance utilization data with library details
    utilization = []
    for util in utilization_raw:
        library = Library.query.get(util['library_id'])
        util['city'] = library.city if library else 'N/A'
        util['state'] = library.state if library else 'N/A'
        utilization.append(util)
    
    # Get daily booking trends
    daily_trends = AnalyticsService.get_daily_bookings(days=30)
    
    # Get library rankings
    top_libraries = AnalyticsService.get_library_rankings(metric='bookings', days=30)
    
    # Get user statistics
    user_stats = AnalyticsService.get_user_statistics()
    
    # Get pending gallery count
    pending_gallery_count = GalleryImage.query.filter_by(
        status=GalleryStatus.pending
    ).count()
    
    return render_template(
        'csr_dashboard.html',
        summary=summary,
        utilization=utilization,
        daily_trends=daily_trends,
        top_libraries=top_libraries,
        user_stats=user_stats,
        pending_gallery_count=pending_gallery_count
    )

@csr_admin_bp.route('/libraries')
@csr_super_admin_required
def manage_libraries():
    """Manage all libraries (CRUD operations)"""
    libraries = Library.query.order_by(Library.created_at.desc()).all()
    
    # Get stats for each library
    library_stats = {}
    for library in libraries:
        total_seats = Seat.query.filter_by(library_id=library.id).count()
        total_bookings = Booking.query.filter_by(library_id=library.id).count()
        active_bookings = Booking.query.filter_by(
            library_id=library.id,
            status=BookingStatus.booked
        ).filter(Booking.date >= date.today()).count()
        
        # Count reserved seats by type (will be 0 if categories don't exist yet)
        try:
            researcher_seats = Seat.query.filter_by(
                library_id=library.id,
                category=SeatCategory.researcher
            ).count()
            
            staff_seats = Seat.query.filter_by(
                library_id=library.id,
                category=SeatCategory.staff
            ).count()
        except AttributeError:
            # Old database without new categories
            researcher_seats = 0
            staff_seats = 0
        
        library_stats[library.id] = {
            'total_seats': total_seats,
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'researcher_seats': researcher_seats,
            'staff_seats': staff_seats
        }
    
    return render_template(
        'csr_libraries.html',
        libraries=libraries,
        library_stats=library_stats
    )

@csr_admin_bp.route('/libraries/create', methods=['GET', 'POST'])
@csr_super_admin_required
def create_library():
    """Create a new library with auto-setup"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        slug = request.form.get('slug', '').strip().lower()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        csr_partner = request.form.get('csr_partner', 'Kaluwala Constructions Pvt Ltd').strip()
        
        # Number of seats to create
        num_seats = request.form.get('num_seats', 60, type=int)
        reserved_percentage = request.form.get('reserved_percentage', 25, type=int)
        
        # Operating hours
        opening_time_str = request.form.get('opening_time', '09:00')
        closing_time_str = request.form.get('closing_time', '21:00')
        slot_duration = request.form.get('slot_duration', 60, type=int)
        
        # Admin user details
        admin_username = request.form.get('admin_username', '').strip()
        admin_email = request.form.get('admin_email', '').strip()
        admin_password = request.form.get('admin_password', '').strip()
        
        # Validate required fields
        if not all([name, slug, address, city, state, pincode]):
            flash('Please fill in all required fields', 'error')
            return render_template('csr_library_create.html')
        
        # Check if slug already exists
        if Library.query.filter_by(slug=slug).first():
            flash('Library slug already exists. Please choose a different one.', 'error')
            return render_template('csr_library_create.html')
        
        try:
            # Parse times
            opening_time = datetime.strptime(opening_time_str, '%H:%M').time()
            closing_time = datetime.strptime(closing_time_str, '%H:%M').time()
            
            # Create library
            library = Library(
                name=name,
                slug=slug,
                address=address,
                city=city,
                state=state,
                pincode=pincode,
                contact_email=contact_email,
                contact_phone=contact_phone,
                csr_partner=csr_partner
            )
            db.session.add(library)
            db.session.flush()  # Get library.id
            
            # Create seats
            reserved_count = int(num_seats * reserved_percentage / 100)
            general_count = num_seats - reserved_count
            
            for i in range(1, num_seats + 1):
                category = SeatCategory.reserved if i > general_count else SeatCategory.general
                seat = Seat(
                    library_id=library.id,
                    number=str(i),
                    category=category,
                    in_maintenance=False
                )
                db.session.add(seat)
            
            # Create system settings
            settings = SystemSettings(
                library_id=library.id,
                opening_time=opening_time,
                closing_time=closing_time,
                slot_duration=slot_duration,
                login_marquee=f'Welcome to {library.name}',
                maintenance_mode=False
            )
            db.session.add(settings)
            
            # Create admin user if provided
            if admin_username and admin_email and admin_password:
                # Check if username exists
                if not User.query.filter_by(username=admin_username).first():
                    admin_user = User(
                        username=admin_username,
                        email=admin_email,
                        home_library_id=library.id,
                        is_active=True
                    )
                    admin_user.set_password(admin_password)
                    db.session.add(admin_user)
                    db.session.flush()
                    
                    # Assign as library admin
                    admin_assignment = LibraryAdmin(
                        user_id=admin_user.id,
                        library_id=library.id,
                        role=AdminRole.admin
                    )
                    db.session.add(admin_assignment)
            
            db.session.commit()
            
            flash(f'Library "{name}" created successfully with {num_seats} seats!', 'success')
            return redirect(url_for('csr_admin.manage_libraries'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating library: {str(e)}', 'error')
            return render_template('csr_library_create.html')
    
    return render_template('csr_library_create.html')

@csr_admin_bp.route('/libraries/<int:library_id>/edit', methods=['GET', 'POST'])
@csr_super_admin_required
def edit_library(library_id):
    """Edit library details"""
    library = Library.query.get_or_404(library_id)
    
    if request.method == 'POST':
        library.name = request.form.get('name', '').strip()
        library.address = request.form.get('address', '').strip()
        library.city = request.form.get('city', '').strip()
        library.state = request.form.get('state', '').strip()
        library.pincode = request.form.get('pincode', '').strip()
        library.contact_email = request.form.get('contact_email', '').strip()
        library.contact_phone = request.form.get('contact_phone', '').strip()
        library.csr_partner = request.form.get('csr_partner', '').strip()
        
        db.session.commit()
        flash(f'Library "{library.name}" updated successfully', 'success')
        return redirect(url_for('csr_admin.manage_libraries'))
    
    return render_template('csr_library_edit.html', library=library)

@csr_admin_bp.route('/libraries/<int:library_id>/delete', methods=['POST'])
@csr_super_admin_required
def delete_library(library_id):
    """Delete a library (cascades to seats, bookings, etc.)"""
    library = Library.query.get_or_404(library_id)
    
    library_name = library.name
    db.session.delete(library)
    db.session.commit()
    
    flash(f'Library "{library_name}" has been deleted', 'success')
    return redirect(url_for('csr_admin.manage_libraries'))

@csr_admin_bp.route('/libraries/<int:library_id>/update-seats', methods=['POST'])
@csr_super_admin_required
def update_seats(library_id):
    """Update seat capacity for a library"""
    library = Library.query.get_or_404(library_id)
    
    new_total = request.form.get('total_seats', type=int)
    
    if not new_total or new_total < 10 or new_total > 500:
        flash('Seat capacity must be between 10 and 500', 'error')
        return redirect(url_for('csr_admin.manage_libraries'))
    
    # Get current seat count
    current_seats = Seat.query.filter_by(library_id=library_id).order_by(
        Seat.number.cast(db.Integer)
    ).all()
    current_count = len(current_seats)
    
    try:
        if new_total > current_count:
            # Add more seats
            seats_to_add = new_total - current_count
            for i in range(seats_to_add):
                new_number = current_count + i + 1
                # 75% general, 25% reserved
                category = SeatCategory.general if new_number <= (new_total * 0.75) else SeatCategory.reserved
                
                new_seat = Seat(
                    library_id=library_id,
                    number=str(new_number),
                    category=category,
                    in_maintenance=False
                )
                db.session.add(new_seat)
            
            db.session.commit()
            flash(f'Added {seats_to_add} seats to {library.name}. Total: {new_total}', 'success')
        
        elif new_total < current_count:
            # Remove seats (from the end, but only if no active bookings)
            seats_to_remove = current_count - new_total
            seats_to_delete = current_seats[-seats_to_remove:]
            
            # Check if any of these seats have active bookings
            for seat in seats_to_delete:
                active_bookings = Booking.query.filter_by(
                    seat_id=seat.id,
                    status=BookingStatus.booked
                ).filter(Booking.date >= date.today()).count()
                
                if active_bookings > 0:
                    flash(f'Cannot remove seats with active bookings. Seat {seat.number} has {active_bookings} active booking(s).', 'error')
                    return redirect(url_for('csr_admin.manage_libraries'))
            
            # Safe to delete
            for seat in seats_to_delete:
                db.session.delete(seat)
            
            db.session.commit()
            flash(f'Removed {seats_to_remove} seats from {library.name}. Total: {new_total}', 'success')
        
        else:
            flash('Seat count is already at this value', 'info')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating seats: {str(e)}', 'error')
    
    return redirect(url_for('csr_admin.manage_libraries'))

@csr_admin_bp.route('/libraries/<int:library_id>/update-reservations', methods=['POST'])
@csr_super_admin_required
def update_reservations(library_id):
    """Update seat reservations for researchers and staff"""
    library = Library.query.get_or_404(library_id)
    
    researcher_count = request.form.get('researcher_seats', 0, type=int)
    staff_count = request.form.get('staff_seats', 0, type=int)
    
    # Get total seats
    total_seats = Seat.query.filter_by(library_id=library_id).count()
    
    # Validate
    if researcher_count < 0 or staff_count < 0:
        flash('Reservation counts cannot be negative', 'error')
        return redirect(url_for('csr_admin.manage_libraries'))
    
    if researcher_count + staff_count > total_seats:
        flash(f'Total reservations ({researcher_count + staff_count}) cannot exceed total seats ({total_seats})', 'error')
        return redirect(url_for('csr_admin.manage_libraries'))
    
    try:
        # Get all general seats ordered by number
        general_seats = Seat.query.filter_by(
            library_id=library_id,
            category=SeatCategory.general
        ).order_by(Seat.number.cast(db.Integer)).all()
        
        # Get current reserved seats
        current_researcher = Seat.query.filter_by(
            library_id=library_id,
            category=SeatCategory.researcher
        ).all()
        
        current_staff = Seat.query.filter_by(
            library_id=library_id,
            category=SeatCategory.staff
        ).all()
        
        # First, convert all researcher and staff seats back to general
        for seat in current_researcher + current_staff:
            # Check if seat has active bookings
            active_bookings = Booking.query.filter_by(
                seat_id=seat.id,
                status=BookingStatus.booked
            ).filter(Booking.date >= date.today()).count()
            
            if active_bookings == 0:
                seat.category = SeatCategory.general
        
        db.session.flush()
        
        # Get fresh list of general seats
        available_general = Seat.query.filter_by(
            library_id=library_id,
            category=SeatCategory.general
        ).order_by(Seat.number.cast(db.Integer)).all()
        
        if len(available_general) < (researcher_count + staff_count):
            flash('Not enough available seats to allocate reservations. Some seats have active bookings.', 'error')
            db.session.rollback()
            return redirect(url_for('csr_admin.manage_libraries'))
        
        # Allocate researcher seats from the end
        researcher_allocated = 0
        for seat in reversed(available_general):
            if researcher_allocated >= researcher_count:
                break
            seat.category = SeatCategory.researcher
            researcher_allocated += 1
        
        # Allocate staff seats from the end (after researcher seats)
        remaining_general = [s for s in available_general if s.category == SeatCategory.general]
        staff_allocated = 0
        for seat in reversed(remaining_general):
            if staff_allocated >= staff_count:
                break
            seat.category = SeatCategory.staff
            staff_allocated += 1
        
        db.session.commit()
        
        flash(f'Seat reservations updated: {researcher_count} for researchers, {staff_count} for staff', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating reservations: {str(e)}', 'error')
    
    return redirect(url_for('csr_admin.manage_libraries'))

@csr_admin_bp.route('/admins')
@csr_super_admin_required
def manage_admins():
    """Manage library administrators"""
    # Get all library admin assignments
    assignments = LibraryAdmin.query.join(User).join(Library).all()
    
    # Get all libraries for assignment form
    libraries = Library.query.all()
    
    # Get all users (potential admins)
    users = User.query.filter_by(is_active=True).all()
    
    return render_template(
        'csr_admins.html',
        assignments=assignments,
        libraries=libraries,
        users=users
    )

@csr_admin_bp.route('/admins/assign', methods=['POST'])
@csr_super_admin_required
def assign_admin():
    """Assign a user as admin to a library"""
    user_id = request.form.get('user_id', type=int)
    library_id = request.form.get('library_id', type=int)
    role = request.form.get('role', 'staff')
    
    if not user_id or not library_id:
        flash('Please select both user and library', 'error')
        return redirect(url_for('csr_admin.manage_admins'))
    
    # Check if assignment already exists
    existing = LibraryAdmin.query.filter_by(
        user_id=user_id,
        library_id=library_id
    ).first()
    
    if existing:
        flash('This user is already assigned to this library', 'error')
        return redirect(url_for('csr_admin.manage_admins'))
    
    # Create assignment
    role_enum = AdminRole.admin if role == 'admin' else AdminRole.staff
    assignment = LibraryAdmin(
        user_id=user_id,
        library_id=library_id,
        role=role_enum
    )
    
    db.session.add(assignment)
    db.session.commit()
    
    user = User.query.get(user_id)
    library = Library.query.get(library_id)
    flash(f'{user.username} assigned as {role} to {library.name}', 'success')
    
    return redirect(url_for('csr_admin.manage_admins'))

@csr_admin_bp.route('/admins/<int:user_id>/<int:library_id>/remove', methods=['POST'])
@csr_super_admin_required
def remove_admin(user_id, library_id):
    """Remove admin assignment"""
    assignment = LibraryAdmin.query.filter_by(
        user_id=user_id,
        library_id=library_id
    ).first_or_404()
    
    user = User.query.get(user_id)
    library = Library.query.get(library_id)
    
    db.session.delete(assignment)
    db.session.commit()
    
    flash(f'{user.username} removed from {library.name}', 'success')
    return redirect(url_for('csr_admin.manage_admins'))

@csr_admin_bp.route('/analytics')
@csr_super_admin_required
def analytics():
    """Detailed analytics page"""
    days = request.args.get('days', 30, type=int)
    
    # Get network summary
    summary = AnalyticsService.get_network_summary()
    
    # Get comprehensive analytics
    utilization = AnalyticsService.get_library_utilization(days=days) or []
    daily_trends = AnalyticsService.get_daily_bookings(days=days) or []
    monthly_data = AnalyticsService.get_monthly_bookings(months=6) or []
    peak_hours = AnalyticsService.get_peak_hours(days=days) or []
    status_breakdown = AnalyticsService.get_booking_status_breakdown() or []
    
    # Get rankings (just pass utilization data sorted by bookings)
    rankings = sorted(utilization, key=lambda x: x.get('total_bookings', 0), reverse=True)[:10] if utilization else []
    
    return render_template(
        'csr_analytics.html',
        summary=summary,
        utilization=utilization,
        daily_trends=daily_trends,
        monthly_data=monthly_data,
        peak_hours=peak_hours,
        status_breakdown=status_breakdown,
        rankings=rankings,
        days=days
    )

@csr_admin_bp.route('/export/bookings')
@csr_super_admin_required
def export_bookings():
    """Export all bookings to CSV"""
    return AnalyticsService.export_bookings_csv()

@csr_admin_bp.route('/export/libraries')
@csr_super_admin_required
def export_libraries():
    """Export all libraries to CSV"""
    return AnalyticsService.export_libraries_csv()

@csr_admin_bp.route('/api/utilization')
@csr_super_admin_required
def api_utilization():
    """API endpoint for utilization data"""
    days = request.args.get('days', 30, type=int)
    data = AnalyticsService.get_library_utilization(days=days)
    return jsonify(data)

@csr_admin_bp.route('/api/daily-trends')
@csr_super_admin_required
def api_daily_trends():
    """API endpoint for daily booking trends"""
    days = request.args.get('days', 30, type=int)
    data = AnalyticsService.get_daily_bookings(days=days)
    return jsonify(data)

@csr_admin_bp.route('/gallery/pending')
@csr_super_admin_required
def gallery_approvals():
    """View pending gallery images"""
    pending_images = GalleryImage.query.filter_by(
        status=GalleryStatus.pending
    ).order_by(GalleryImage.uploaded_at.desc()).all()
    
    return render_template('csr_gallery_approvals.html', pending_images=pending_images)

@csr_admin_bp.route('/gallery/approve', methods=['POST'])
@csr_super_admin_required
def approve_gallery_image():
    """Approve or reject a gallery image"""
    image_id = request.form.get('image_id', type=int)
    action = request.form.get('action')
    
    image = GalleryImage.query.get_or_404(image_id)
    
    if action == 'approve':
        image.status = GalleryStatus.approved
        image.reviewed_by = current_user.id
        image.reviewed_at = datetime.utcnow()
        flash(f'Photo "{image.caption}" approved!', 'success')
    
    elif action == 'reject':
        image.status = GalleryStatus.rejected
        image.reviewed_by = current_user.id
        image.reviewed_at = datetime.utcnow()
        image.rejection_reason = request.form.get('rejection_reason', '')
        flash(f'Photo "{image.caption}" rejected', 'info')
    
    db.session.commit()
    return redirect(url_for('csr_admin.gallery_approvals'))

