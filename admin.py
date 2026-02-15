"""
Admin Blueprint for Library Administration
Handles library-specific admin functions
"""

import os
from functools import wraps
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Library, Seat, SystemSettings, Booking, User, LibraryAdmin, AdminRole, BookingStatus, SeatCategory, ApprovalStatus, GalleryImage, GalleryStatus
from sqlalchemy import func, and_, extract

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# File upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def library_admin_required(f):
    """Decorator to ensure user is admin of current library"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Get library slug from kwargs or g
        slug = kwargs.get('slug') or getattr(g, 'current_library', None)
        
        if not slug:
            flash('Library context required', 'error')
            return redirect(url_for('index'))
        
        # Get library
        if isinstance(slug, str):
            library = Library.query.filter_by(slug=slug).first()
        else:
            library = slug
            
        if not library:
            flash('Library not found', 'error')
            return redirect(url_for('index'))
        
        # Check if user is admin of this library
        if not current_user.is_admin_of(library.id):
            flash('You do not have admin access to this library', 'error')
            return redirect(url_for('dashboard', slug=library.slug))
        
        # Store library in g for use in view
        g.admin_library = library
        return f(*args, **kwargs)
    
    return decorated_function

@admin_bp.route('/<slug>')
@library_admin_required
def dashboard(slug):
    """Library admin dashboard"""
    library = g.admin_library
    
    # Get statistics
    total_seats = Seat.query.filter_by(library_id=library.id).count()
    maintenance_seats = Seat.query.filter_by(library_id=library.id, in_maintenance=True).count()
    
    # Today's bookings
    today_bookings = Booking.query.filter_by(
        library_id=library.id,
        date=date.today(),
        status=BookingStatus.booked
    ).count()
    
    # Total bookings this month
    current_month = date.today().replace(day=1)
    month_bookings = Booking.query.filter(
        Booking.library_id == library.id,
        Booking.date >= current_month
    ).count()
    
    # Active users (users who have made bookings)
    active_users = db.session.query(func.count(func.distinct(Booking.user_id))).filter(
        Booking.library_id == library.id
    ).scalar()
    
    # Recent bookings
    recent_bookings = Booking.query.filter_by(
        library_id=library.id
    ).order_by(Booking.created_at.desc()).limit(10).all()
    
    # Get settings
    settings = SystemSettings.query.filter_by(library_id=library.id).first()
    
    # Get pending users count
    pending_count = User.query.filter_by(
        home_library_id=library.id,
        approval_status=ApprovalStatus.pending
    ).count()
    
    return render_template(
        'admin_dashboard.html',
        library=library,
        total_seats=total_seats,
        maintenance_seats=maintenance_seats,
        today_bookings=today_bookings,
        month_bookings=month_bookings,
        active_users=active_users,
        recent_bookings=recent_bookings,
        settings=settings,
        pending_count=pending_count
    )

@admin_bp.route('/<slug>/seats')
@library_admin_required
def manage_seats(slug):
    """Manage seats - view and toggle maintenance"""
    library = g.admin_library
    
    # Get all seats
    seats = Seat.query.filter_by(library_id=library.id).order_by(
        Seat.number.cast(db.Integer)
    ).all()
    
    # Get booking counts for each seat
    seat_stats = {}
    for seat in seats:
        booking_count = Booking.query.filter_by(seat_id=seat.id).count()
        seat_stats[seat.id] = booking_count
    
    return render_template(
        'admin_seats.html',
        library=library,
        seats=seats,
        seat_stats=seat_stats
    )

@admin_bp.route('/<slug>/seats/<int:seat_id>/toggle-maintenance', methods=['POST'])
@library_admin_required
def toggle_maintenance(slug, seat_id):
    """Toggle seat maintenance status"""
    library = g.admin_library
    
    seat = Seat.query.filter_by(id=seat_id, library_id=library.id).first()
    if not seat:
        flash('Seat not found', 'error')
        return redirect(url_for('admin.manage_seats', slug=slug))
    
    # Toggle maintenance
    seat.in_maintenance = not seat.in_maintenance
    db.session.commit()
    
    status = "under maintenance" if seat.in_maintenance else "available"
    flash(f'Seat {seat.number} is now {status}', 'success')
    
    return redirect(url_for('admin.manage_seats', slug=slug))

@admin_bp.route('/<slug>/settings', methods=['GET', 'POST'])
@library_admin_required
def manage_settings(slug):
    """Manage library settings"""
    library = g.admin_library
    
    settings = SystemSettings.query.filter_by(library_id=library.id).first()
    if not settings:
        flash('Settings not found for this library', 'error')
        return redirect(url_for('admin.dashboard', slug=slug))
    
    if request.method == 'POST':
        # Get form data
        opening_time_str = request.form.get('opening_time')
        closing_time_str = request.form.get('closing_time')
        slot_duration = request.form.get('slot_duration', type=int)
        login_marquee = request.form.get('login_marquee', '').strip()
        maintenance_mode = request.form.get('maintenance_mode') == 'on'
        
        # Validate
        try:
            opening_time = datetime.strptime(opening_time_str, '%H:%M').time()
            closing_time = datetime.strptime(closing_time_str, '%H:%M').time()
        except:
            flash('Invalid time format', 'error')
            return render_template('admin_settings.html', library=library, settings=settings)
        
        if opening_time >= closing_time:
            flash('Opening time must be before closing time', 'error')
            return render_template('admin_settings.html', library=library, settings=settings)
        
        if slot_duration < 15 or slot_duration > 240:
            flash('Slot duration must be between 15 and 240 minutes', 'error')
            return render_template('admin_settings.html', library=library, settings=settings)
        
        # Update settings
        settings.opening_time = opening_time
        settings.closing_time = closing_time
        settings.slot_duration = slot_duration
        settings.login_marquee = login_marquee
        settings.maintenance_mode = maintenance_mode
        
        db.session.commit()
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin.manage_settings', slug=slug))
    
    return render_template('admin_settings.html', library=library, settings=settings)

@admin_bp.route('/<slug>/reports')
@library_admin_required
def reports(slug):
    """View library reports and analytics"""
    library = g.admin_library
    
    # Date range from query params
    days = request.args.get('days', 30, type=int)
    start_date = date.today() - timedelta(days=days)
    
    # Total bookings in period
    total_bookings = Booking.query.filter(
        Booking.library_id == library.id,
        Booking.date >= start_date
    ).count()
    
    # Bookings by status
    bookings_by_status = db.session.query(
        Booking.status,
        func.count(Booking.id)
    ).filter(
        Booking.library_id == library.id,
        Booking.date >= start_date
    ).group_by(Booking.status).all()
    
    status_stats = {status.value: 0 for status in BookingStatus}
    for status, count in bookings_by_status:
        status_stats[status.value] = count
    
    # Daily bookings for chart
    daily_bookings = db.session.query(
        Booking.date,
        func.count(Booking.id)
    ).filter(
        Booking.library_id == library.id,
        Booking.date >= start_date
    ).group_by(Booking.date).order_by(Booking.date).all()
    
    # Seat utilization
    seat_utilization = db.session.query(
        Seat.number,
        func.count(Booking.id)
    ).join(Booking).filter(
        Seat.library_id == library.id,
        Booking.date >= start_date
    ).group_by(Seat.id).order_by(func.count(Booking.id).desc()).limit(10).all()
    
    # Peak hours
    peak_hours = db.session.query(
        func.strftime('%H', Booking.time_slot).label('hour'),
        func.count(Booking.id)
    ).filter(
        Booking.library_id == library.id,
        Booking.date >= start_date
    ).group_by('hour').order_by(func.count(Booking.id).desc()).all()
    
    # Top users
    top_users = db.session.query(
        User.username,
        func.count(Booking.id)
    ).join(Booking).filter(
        Booking.library_id == library.id,
        Booking.date >= start_date
    ).group_by(User.id).order_by(func.count(Booking.id).desc()).limit(10).all()
    
    return render_template(
        'admin_reports.html',
        library=library,
        days=days,
        start_date=start_date,
        total_bookings=total_bookings,
        status_stats=status_stats,
        daily_bookings=daily_bookings,
        seat_utilization=seat_utilization,
        peak_hours=peak_hours,
        top_users=top_users
    )

@admin_bp.route('/<slug>/users')
@library_admin_required
def manage_users(slug):
    """Manage library users and staff"""
    library = g.admin_library
    
    # Get all users with bookings at this library
    users_with_bookings = db.session.query(User).join(Booking).filter(
        Booking.library_id == library.id
    ).distinct().all()
    
    # Get stats for each user
    user_stats = {}
    total_bookings = 0
    
    for user in users_with_bookings:
        total = Booking.query.filter_by(
            user_id=user.id,
            library_id=library.id
        ).count()
        
        active = Booking.query.filter_by(
            user_id=user.id,
            library_id=library.id,
            status=BookingStatus.booked
        ).filter(Booking.date >= date.today()).count()
        
        last_booking_obj = Booking.query.filter_by(
            user_id=user.id,
            library_id=library.id
        ).order_by(Booking.date.desc()).first()
        
        user_stats[user] = {
            'total_bookings': total,
            'active_bookings': active,
            'last_booking': last_booking_obj.date if last_booking_obj else None
        }
        total_bookings += total
    
    # Get staff assignments
    staff = LibraryAdmin.query.filter_by(library_id=library.id).all()
    
    return render_template(
        'admin_users.html',
        library=library,
        users_with_bookings=users_with_bookings,
        user_stats=user_stats,
        staff=staff,
        total_bookings=total_bookings
    )

@admin_bp.route('/<slug>/bookings')
@library_admin_required
def all_bookings(slug):
    """View all bookings for the library"""
    library = g.admin_library
    
    # Filter parameters
    status_filter = request.args.get('status', 'all')
    date_filter = request.args.get('date', '')
    
    # Base query
    query = Booking.query.filter_by(library_id=library.id)
    
    # Apply filters
    if status_filter != 'all':
        try:
            status_enum = BookingStatus[status_filter]
            query = query.filter_by(status=status_enum)
        except:
            pass
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(date=filter_date)
        except:
            pass
    
    # Get bookings
    bookings = query.order_by(Booking.date.desc(), Booking.time_slot.desc()).limit(100).all()
    
    return render_template(
        'admin_bookings.html',
        library=library,
        bookings=bookings,
        status_filter=status_filter,
        date_filter=date_filter
    )

@admin_bp.route('/<slug>/bookings/<int:booking_id>/cancel', methods=['POST'])
@library_admin_required
def cancel_user_booking(slug, booking_id):
    """Admin cancel any booking"""
    library = g.admin_library
    
    booking = Booking.query.filter_by(id=booking_id, library_id=library.id).first()
    if not booking:
        flash('Booking not found', 'error')
        return redirect(url_for('admin.all_bookings', slug=slug))
    
    if booking.status != BookingStatus.booked:
        flash('Only active bookings can be cancelled', 'error')
        return redirect(url_for('admin.all_bookings', slug=slug))
    
    booking.status = BookingStatus.cancelled
    db.session.commit()
    
    flash(f'Booking #{booking.id} has been cancelled', 'success')
    return redirect(url_for('admin.all_bookings', slug=slug))

@admin_bp.route('/<slug>/api/stats')
@library_admin_required
def api_stats(slug):
    """API endpoint for dashboard statistics"""
    library = g.admin_library
    
    # Get date range
    days = request.args.get('days', 7, type=int)
    start_date = date.today() - timedelta(days=days)
    
    # Daily bookings
    daily_data = db.session.query(
        Booking.date,
        func.count(Booking.id)
    ).filter(
        Booking.library_id == library.id,
        Booking.date >= start_date,
        Booking.date <= date.today()
    ).group_by(Booking.date).order_by(Booking.date).all()
    
    # Format for chart
    dates = []
    counts = []
    for booking_date, count in daily_data:
        dates.append(booking_date.strftime('%Y-%m-%d'))
        counts.append(count)
    
    return jsonify({
        'dates': dates,
        'bookings': counts
    })

@admin_bp.route('/<slug>/approvals')
@library_admin_required
def pending_approvals(slug):
    """View pending user registrations"""
    library = g.admin_library
    
    # Get pending users for this library
    pending_users = User.query.filter_by(
        home_library_id=library.id,
        approval_status=ApprovalStatus.pending
    ).order_by(User.created_at.desc()).all()
    
    # Get recently approved (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    approved_users = User.query.filter_by(
        home_library_id=library.id,
        approval_status=ApprovalStatus.approved
    ).filter(
        User.approved_at >= thirty_days_ago
    ).order_by(User.approved_at.desc()).all()
    
    # Get recently rejected (last 30 days)
    rejected_users = User.query.filter_by(
        home_library_id=library.id,
        approval_status=ApprovalStatus.rejected
    ).filter(
        User.approved_at >= thirty_days_ago
    ).order_by(User.approved_at.desc()).all()
    
    return render_template(
        'admin_approvals.html',
        library=library,
        pending_users=pending_users,
        approved_users=approved_users,
        rejected_users=rejected_users,
        User=User
    )

@admin_bp.route('/<slug>/pending-users')
@library_admin_required
def pending_users(slug):
    """View and approve pending user registrations"""
    library = g.admin_library
    
    # Get pending users for this library
    pending = User.query.filter_by(
        home_library_id=library.id,
        approval_status=ApprovalStatus.pending
    ).order_by(User.created_at.desc()).all()
    
    return render_template(
        'admin_pending_users.html',
        library=library,
        pending_users=pending,
        now=datetime.utcnow()
    )

@admin_bp.route('/<slug>/approve-user/<int:user_id>', methods=['POST'])
@library_admin_required
def approve_user(slug, user_id):
    """Approve a pending user and assign role"""
    library = g.admin_library
    user = User.query.get_or_404(user_id)
    
    # Verify user is for this library
    if user.home_library_id != library.id:
        flash('You can only approve users for your library', 'error')
        return redirect(url_for('admin.pending_users', slug=slug))
    
    # Verify user is pending
    if user.approval_status != ApprovalStatus.pending:
        flash('This user has already been reviewed', 'error')
        return redirect(url_for('admin.pending_users', slug=slug))
    
    # Get selected role from form
    selected_role = request.form.get('user_role', 'student')
    
    try:
        # Import UserRole if not already imported
        from models import UserRole
        
        # Map string to UserRole enum
        if selected_role == 'student':
            user.user_role = UserRole.student
        elif selected_role == 'researcher':
            user.user_role = UserRole.researcher
        elif selected_role == 'staff':
            user.user_role = UserRole.staff
        elif selected_role == 'library_admin':
            user.user_role = UserRole.library_admin
            # If assigning as library admin, create LibraryAdmin record
            existing_admin = LibraryAdmin.query.filter_by(
                user_id=user.id,
                library_id=library.id
            ).first()
            if not existing_admin:
                admin_assignment = LibraryAdmin(
                    user_id=user.id,
                    library_id=library.id,
                    role=AdminRole.admin
                )
                db.session.add(admin_assignment)
        else:
            user.user_role = UserRole.student  # Default fallback
        
        # Approve user
        user.approval_status = ApprovalStatus.approved
        user.is_active = True
        user.approved_by = current_user.id
        user.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        # Send approval email
        try:
            from services.email_service import EmailService
            EmailService.send_approval_email(user, library)
        except Exception as e:
            print(f"Email error: {e}")
        
        role_display = selected_role.replace('_', ' ').title()
        flash(f'✅ User {user.username} approved as {role_display}! Approval email sent.', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving user: {str(e)}', 'error')
    
    return redirect(url_for('admin.pending_users', slug=slug))

@admin_bp.route('/<slug>/reject-user/<int:user_id>', methods=['POST'])
@library_admin_required
def reject_user(slug, user_id):
    """Reject a pending user registration"""
    library = g.admin_library
    user = User.query.get_or_404(user_id)
    
    # Verify user is for this library
    if user.home_library_id != library.id:
        flash('You can only reject users for your library', 'error')
        return redirect(url_for('admin.pending_approvals', slug=slug))
    
    # Verify user is pending
    if user.approval_status != ApprovalStatus.pending:
        flash('This user has already been reviewed', 'error')
        return redirect(url_for('admin.pending_approvals', slug=slug))
    
    # Reject user
    user.approval_status = ApprovalStatus.rejected
    user.is_active = False
    user.approved_by = current_user.id
    user.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    flash(f'User {user.username} has been rejected', 'info')
    return redirect(url_for('admin.pending_approvals', slug=slug))

@admin_bp.route('/<slug>/gallery', methods=['GET', 'POST'])
@library_admin_required
def gallery(slug):
    """Library admin gallery management"""
    library = g.admin_library
    
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No image file provided', 'error')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            if file_size > MAX_FILE_SIZE:
                flash('File too large. Maximum size is 5MB', 'error')
                return redirect(request.url)
            file.seek(0)
            
            # Generate unique filename
            import uuid
            ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join('static', 'gallery', filename)
            
            # Save file
            file.save(filepath)
            
            # Create database entry
            gallery_image = GalleryImage(
                library_id=library.id,
                uploaded_by=current_user.id,
                filename=filename,
                original_filename=secure_filename(file.filename),
                file_path=filepath,
                caption=request.form.get('caption', ''),
                description=request.form.get('description', ''),
                file_size=file_size,
                status=GalleryStatus.pending
            )
            
            db.session.add(gallery_image)
            db.session.commit()
            
            flash('Photo uploaded! Waiting for CSR admin approval.', 'success')
            return redirect(url_for('admin.gallery', slug=slug))
        else:
            flash('Invalid file type. Only PNG, JPG, JPEG, GIF allowed', 'error')
            return redirect(request.url)
    
    # Get user's images for this library
    my_images = GalleryImage.query.filter_by(
        library_id=library.id,
        uploaded_by=current_user.id
    ).order_by(GalleryImage.uploaded_at.desc()).all()
    
    return render_template('admin_gallery.html', library=library, my_images=my_images)

@admin_bp.route('/<slug>/gallery/delete/<int:image_id>', methods=['POST'])
@library_admin_required
def delete_gallery_image(slug, image_id):
    """Delete a gallery image"""
    library = g.admin_library
    
    image = GalleryImage.query.get_or_404(image_id)
    
    # Verify ownership
    if image.library_id != library.id or image.uploaded_by != current_user.id:
        flash('You can only delete your own images', 'error')
        return redirect(url_for('admin.gallery', slug=slug))
    
    # Delete file
    if os.path.exists(image.file_path):
        os.remove(image.file_path)
    
    db.session.delete(image)
    db.session.commit()
    
    flash('Photo deleted successfully', 'success')
    return redirect(url_for('admin.gallery', slug=slug))

# ============= PDF REPORTS =============

@admin_bp.route('/<slug>/reports/pdf', methods=['GET'])
@library_admin_required
def download_pdf_report(slug):
    """Generate and download PDF report"""
    from flask import send_file
    from services.pdf_service import PDFReportService
    from datetime import timedelta
    
    library = g.admin_library
    
    # Default: Last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Generate PDF
    pdf_buffer = PDFReportService.generate_booking_report(
        library, start_date, end_date
    )
    
    filename = f"{library.slug}_report_{start_date}_{end_date}.pdf"
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

# ============= BULK OPERATIONS =============

@admin_bp.route('/<slug>/bulk-operations')
@library_admin_required
def bulk_operations(slug):
    """Bulk operations page"""
    from services.bulk_service import BulkOperationsService
    
    library = g.admin_library
    
    # Get statistics
    stats = BulkOperationsService.get_bulk_stats(library.id)
    
    return render_template(
        'admin_bulk_operations.html',
        library=library,
        stats=stats,
        today=date.today().isoformat()
    )

@admin_bp.route('/<slug>/bulk/create-seats', methods=['POST'])
@library_admin_required
def bulk_create_seats(slug):
    """Bulk create seats"""
    from services.bulk_service import BulkOperationsService
    
    library = g.admin_library
    
    start = int(request.form.get('start_number'))
    end = int(request.form.get('end_number'))
    category_str = request.form.get('category')
    
    category = SeatCategory[category_str]
    
    created, errors = BulkOperationsService.bulk_create_seats(
        library.id, start, end, category
    )
    
    if errors:
        flash(f'Created {len(created)} seats. {len(errors)} errors occurred.', 'warning')
    else:
        flash(f'✅ Successfully created {len(created)} seats!', 'success')
    
    return redirect(url_for('admin.bulk_operations', slug=slug))

@admin_bp.route('/<slug>/bulk/update-category', methods=['POST'])
@library_admin_required
def bulk_update_category(slug):
    """Bulk update seat categories"""
    from services.bulk_service import BulkOperationsService
    
    library = g.admin_library
    
    seat_numbers_str = request.form.get('seat_numbers')
    seat_numbers = [n.strip() for n in seat_numbers_str.split(',')]
    category_str = request.form.get('category')
    
    category = SeatCategory[category_str]
    
    updated, errors = BulkOperationsService.bulk_update_seat_category(
        library.id, seat_numbers, category
    )
    
    if errors:
        flash(f'Updated {len(updated)} seats. {len(errors)} errors occurred.', 'warning')
    else:
        flash(f'✅ Updated {len(updated)} seats to {category_str}!', 'success')
    
    return redirect(url_for('admin.bulk_operations', slug=slug))

@admin_bp.route('/<slug>/bulk/toggle-maintenance', methods=['POST'])
@library_admin_required
def bulk_toggle_maintenance(slug):
    """Bulk toggle maintenance mode"""
    from services.bulk_service import BulkOperationsService
    
    library = g.admin_library
    
    seat_numbers_str = request.form.get('seat_numbers')
    seat_numbers = [n.strip() for n in seat_numbers_str.split(',')]
    maintenance = request.form.get('maintenance') == 'true'
    
    updated, errors = BulkOperationsService.bulk_toggle_maintenance(
        library.id, seat_numbers, maintenance
    )
    
    status = 'enabled' if maintenance else 'disabled'
    
    if errors:
        flash(f'Maintenance {status} for {len(updated)} seats. {len(errors)} errors occurred.', 'warning')
    else:
        flash(f'✅ Maintenance {status} for {len(updated)} seats!', 'success')
    
    return redirect(url_for('admin.bulk_operations', slug=slug))

@admin_bp.route('/<slug>/bulk/cancel-bookings', methods=['POST'])
@library_admin_required
def bulk_cancel_bookings(slug):
    """Bulk cancel all bookings for a date"""
    from services.bulk_service import BulkOperationsService
    
    library = g.admin_library
    
    date_str = request.form.get('date')
    booking_date = datetime.fromisoformat(date_str).date()
    
    count = BulkOperationsService.bulk_cancel_bookings(
        library.id, booking_date
    )
    
    flash(f'✅ Cancelled {count} bookings for {date_str}. Email notifications sent to all users.', 'success')
    return redirect(url_for('admin.bulk_operations', slug=slug))

# ============= USER REPORTING / CHECK-IN SYSTEM =============

@admin_bp.route('/<slug>/reporting')
@library_admin_required
def user_reporting(slug):
    """User reporting dashboard - track check-ins"""
    from services.reporting_service import ReportingService
    
    library = g.admin_library
    
    # Get pending reports (users who need to check in)
    pending_reports = ReportingService.get_pending_reports(library.id)
    
    # Get users who reported today
    reported_today = ReportingService.get_reported_today(library.id)
    
    # Get upcoming bookings (arriving in next 30 min)
    upcoming = ReportingService.get_upcoming_bookings_needing_report(library.id)
    
    return render_template(
        'admin_reporting.html',
        library=library,
        pending_reports=pending_reports,
        reported_today=reported_today,
        pending_count=len(pending_reports),
        reported_count=len(reported_today),
        upcoming_count=len(upcoming)
    )

@admin_bp.route('/<slug>/reporting/mark', methods=['POST'])
@library_admin_required
def mark_reported(slug):
    """Mark user as reported/checked-in"""
    from services.reporting_service import ReportingService
    
    library = g.admin_library
    booking_id = request.form.get('booking_id', type=int)
    
    success, message = ReportingService.mark_as_reported(
        booking_id, current_user.id
    )
    
    if success:
        flash(f'✅ {message}', 'success')
    else:
        flash(f'❌ {message}', 'error')
    
    return redirect(url_for('admin.user_reporting', slug=slug))

@admin_bp.route('/<slug>/reporting/auto-cancel', methods=['POST'])
@library_admin_required
def run_auto_cancel(slug):
    """Manually trigger auto-cancellation for no-shows"""
    from services.reporting_service import ReportingService
    
    library = g.admin_library
    
    count = ReportingService.auto_cancel_expired_bookings(library.id)
    
    flash(f'✅ Auto-cancelled {count} no-show bookings', 'info')
    return redirect(url_for('admin.user_reporting', slug=slug))
