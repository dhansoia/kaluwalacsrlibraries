import os
import re
from functools import wraps
from datetime import datetime, date, time, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, g, abort, send_from_directory, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_mail import Mail
from config import Config
from models import db, User, Library, Seat, SystemSettings, Booking, BookingStatus, SeatCategory, ApprovalStatus
from sqlalchemy import and_, or_

# Initialize Flask extensions
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()

def run_auto_migration(app):
    """Run migration automatically if no libraries exist"""
    with app.app_context():
        library_count = Library.query.count()
        if library_count == 0:
            print("\n⚠️  No libraries found. Running auto-migration...")
            print("💡 Tip: You can also run 'python migrate.py' manually\n")
            
            try:
                from migrate import (
                    create_bpsmv_library, 
                    create_seats, 
                    create_system_settings, 
                    create_admin_user
                )
                
                print("📚 Setting up BPSMV Central Library...")
                library = create_bpsmv_library()
                create_seats(library)
                create_system_settings(library)
                create_admin_user(library)
                
                print("✅ Auto-migration complete!\n")
                return True
            except ImportError:
                print("⚠️  migrate.py not found. Please run 'python migrate.py' manually.\n")
                return False
        return False

def library_context_required(f):
    """Decorator to ensure library context is set"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_library') or g.current_library is None:
            flash('Library context is required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def approval_required(f):
    """Decorator to ensure user is approved"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # CSR Super Admins bypass approval
        if current_user.is_csr_super_admin:
            return f(*args, **kwargs)
            
        if current_user.approval_status != ApprovalStatus.approved:
            flash('Your account is pending approval. Please wait for admin approval.', 'warning')
            return redirect(url_for('pending_approval'))
        return f(*args, **kwargs)
    return decorated_function

def generate_time_slots(opening_time, closing_time, slot_duration):
    """Generate list of time slots based on library settings"""
    slots = []
    current = datetime.combine(date.today(), opening_time)
    end = datetime.combine(date.today(), closing_time)
    
    while current < end:
        slots.append(current.time())
        current += timedelta(minutes=slot_duration)
    
    return slots

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Ensure instance folder exists
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"✓ Created instance directory: {instance_path}")
    
    # Ensure static folder exists
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    if not os.path.exists(static_path):
        os.makedirs(static_path)
        print(f"✓ Created static directory: {static_path}")
    
    # Ensure gallery folder exists
    gallery_path = os.path.join(static_path, 'gallery')
    if not os.path.exists(gallery_path):
        os.makedirs(gallery_path)
        print(f"✓ Created gallery directory: {gallery_path}")
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)  # Initialize Flask-Mail
    
    # Register admin blueprint
    from admin import admin_bp
    app.register_blueprint(admin_bp)
    print("✓ Admin blueprint registered")
    
    # Register CSR admin blueprint
    from csr_admin import csr_admin_bp
    app.register_blueprint(csr_admin_bp)
    print("✓ CSR Admin blueprint registered")
    
    # Configure login manager
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return User.query.get(int(user_id))
    
    # Create database tables on first run
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Run auto-migration if needed
        run_auto_migration(app)
    
    @app.before_request
    def detect_library_context():
        """Detect library from URL path and set g.current_library"""
        g.current_library = None
        
        # Extract library slug from path
        path = request.path
        
        # Pattern 1: /slug/... (e.g., /bpsmv/dashboard)
        match = re.match(r'^/([a-z0-9-]+)/', path)
        if match:
            slug = match.group(1)
            # Skip common routes that aren't library slugs
            if slug not in ['login', 'register', 'logout', 'static', 'libraries', 'switch-library', 'health', 'bookings', 'admin', 'csr-admin']:
                library = Library.query.filter_by(slug=slug).first()
                if library:
                    g.current_library = library
                    return
        
        # Pattern 2: /libraries/slug (e.g., /libraries/bpsmv)
        match = re.match(r'^/libraries/([a-z0-9-]+)', path)
        if match:
            slug = match.group(1)
            library = Library.query.filter_by(slug=slug).first()
            if library:
                g.current_library = library
    
    @app.context_processor
    def inject_library():
        """Inject current_library into all templates"""
        return {
            'current_library': g.get('current_library', None)
        }
    
    @app.context_processor
    def inject_rules_modal():
        """Inject rules modal flag into all templates"""
        show_rules = False
        
        if current_user.is_authenticated and hasattr(g, 'current_library') and g.current_library:
            from models import UserRulesAcknowledgment
            
            # Check if user has acknowledged rules for this library
            ack = UserRulesAcknowledgment.query.filter_by(
                user_id=current_user.id,
                library_id=g.current_library.id
            ).first()
            
            show_rules = (ack is None)  # Show if not acknowledged
        
        return {'show_rules_modal': show_rules}
    
    # ============= Public Routes =============
    
    # ============= PUBLIC PORTAL ROUTES =============
    
    @app.route('/')
    def index():
        """Public home page with library cards and map"""
        # If already authenticated, redirect to their dashboard
        if current_user.is_authenticated:
            if current_user.is_csr_super_admin:
                return redirect(url_for('csr_admin.dashboard'))
            if current_user.home_library_id:
                home_library = Library.query.get(current_user.home_library_id)
                if home_library:
                    return redirect(url_for('dashboard', slug=home_library.slug))
            return redirect(url_for('switch_library'))
        
        # Show public home page for anonymous users
        from models import GalleryImage, GalleryStatus
        
        # Get all libraries
        libraries = Library.query.all()
        
        # Enhance with counts
        for library in libraries:
            library.total_seats = Seat.query.filter_by(library_id=library.id).count()
        
        # Get network stats
        total_libraries = Library.query.count()
        total_seats = Seat.query.count()
        total_users = User.query.filter_by(is_active=True).count()
        
        return render_template(
            'public_home.html',
            libraries=libraries,
            total_libraries=total_libraries,
            total_seats=total_seats,
            total_users=total_users
        )
    
    @app.route('/libraries/<slug>')
    def library_microsite(slug):
        """Public library microsite with details"""
        from models import GalleryImage, GalleryStatus
        
        library = Library.query.filter_by(slug=slug).first_or_404()
        
        # Get seat count
        library.total_seats = Seat.query.filter_by(library_id=library.id).count()
        
        # Get gallery images
        gallery_images = GalleryImage.query.filter_by(
            library_id=library.id,
            status=GalleryStatus.approved
        ).order_by(GalleryImage.uploaded_at.desc()).limit(12).all()
        
        return render_template(
            'library_microsite.html',
            library=library,
            gallery_images=gallery_images
        )
    
    # ============= AUTHENTICATION ROUTES =============
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page with library pre-selection"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        # Get library from query parameter (for pre-selection from microsite)
        library_slug_param = request.args.get('library')
        preselected_library = None
        
        if library_slug_param:
            preselected_library = Library.query.filter_by(slug=library_slug_param).first()
        
        libraries = Library.query.all()
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            library_slug = request.form.get('library_slug', '').strip()
            
            # Validate inputs
            if not username or not password:
                flash('Username and password are required', 'error')
                return render_template('login.html', libraries=libraries, preselected_library=preselected_library)
            
            # Check user credentials
            user = User.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                flash('Invalid username or password', 'error')
                return render_template('login.html', libraries=libraries, preselected_library=preselected_library)
            
            # Check if user is active
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('login.html', libraries=libraries, preselected_library=preselected_library)
            
            # Login successful
            login_user(user, remember=True)
            flash(f'Welcome back, {user.username}!', 'success')
            
            # CSR Super Admins go to CSR Admin panel
            if user.is_csr_super_admin:
                return redirect(url_for('csr_admin.dashboard'))
            
            # Regular users need library selection
            if not library_slug:
                flash('Please select a library', 'error')
                return render_template('login.html', libraries=libraries, preselected_library=preselected_library)
            
            # Check library exists
            library = Library.query.filter_by(slug=library_slug).first()
            if not library:
                flash('Invalid library selected', 'error')
                return render_template('login.html', libraries=libraries, preselected_library=preselected_library)
            
            # Redirect to library dashboard
            return redirect(url_for('dashboard', slug=library_slug))
        
        return render_template('login.html', libraries=libraries, preselected_library=preselected_library)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Registration page"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        libraries = Library.query.all()
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            home_library_slug = request.form.get('home_library_slug', '').strip()
            
            # Validate inputs
            if not all([username, email, password, confirm_password, home_library_slug]):
                flash('All fields are required', 'error')
                return render_template('register.html', libraries=libraries)
            
            # Check username length
            if len(username) < 3:
                flash('Username must be at least 3 characters', 'error')
                return render_template('register.html', libraries=libraries)
            
            # Check password length
            if len(password) < 6:
                flash('Password must be at least 6 characters', 'error')
                return render_template('register.html', libraries=libraries)
            
            # Check passwords match
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('register.html', libraries=libraries)
            
            # Check library exists
            library = Library.query.filter_by(slug=home_library_slug).first()
            if not library:
                flash('Invalid library selected', 'error')
                return render_template('register.html', libraries=libraries)
            
            # Check if username exists
            if User.query.filter_by(username=username).first():
                flash('Username already taken', 'error')
                return render_template('register.html', libraries=libraries)
            
            # Check if email exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('register.html', libraries=libraries)
            
            # Create new user (pending approval)
            user = User(
                username=username,
                email=email,
                home_library_id=library.id,
                is_active=False,  # Inactive until approved
                approval_status=ApprovalStatus.pending
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Registration successful! Your account is pending approval by {library.name} administrators. You will receive access once approved.', 'info')
            return redirect(url_for('login'))
        
        return render_template('register.html', libraries=libraries)
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout user"""
        logout_user()
        flash('You have been logged out successfully', 'info')
        return redirect(url_for('login'))
    
    @app.route('/switch-library')
    @login_required
    def switch_library():
        """Show library selector"""
        libraries = Library.query.all()
        return render_template('switch_library.html', libraries=libraries)
    
    @app.route('/pending-approval')
    @login_required
    def pending_approval():
        """Show pending approval message"""
        if current_user.is_csr_super_admin or current_user.approval_status == ApprovalStatus.approved:
            return redirect(url_for('index'))
        
        return render_template('pending_approval.html')
    
    @app.route('/acknowledge-rules', methods=['POST'])
    @login_required
    def acknowledge_rules():
        """Acknowledge library rules"""
        from models import UserRulesAcknowledgment
        
        data = request.get_json()
        library_id = data.get('library_id')
        
        if not library_id:
            return jsonify({'success': False, 'error': 'Library ID required'}), 400
        
        # Check if already acknowledged
        existing = UserRulesAcknowledgment.query.filter_by(
            user_id=current_user.id,
            library_id=library_id
        ).first()
        
        if existing:
            return jsonify({'success': True, 'message': 'Already acknowledged'})
        
        # Create acknowledgment
        ack = UserRulesAcknowledgment(
            user_id=current_user.id,
            library_id=library_id,
            ip_address=request.remote_addr
        )
        
        db.session.add(ack)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Rules acknowledged'})
    
    # ============= Library-Specific Routes =============
    
    @app.route('/<slug>/dashboard')
    @login_required
    @library_context_required
    def dashboard(slug):
        """Library dashboard"""
        library = g.current_library
        
        # Get library stats
        total_seats = Seat.query.filter_by(library_id=library.id).count()
        available_seats = Seat.query.filter_by(
            library_id=library.id, 
            in_maintenance=False
        ).count()
        
        # Get user's active bookings for this library
        my_bookings = Booking.query.filter_by(
            user_id=current_user.id,
            library_id=library.id,
            status=BookingStatus.booked
        ).filter(Booking.date >= date.today()).count()
        
        # Get system settings
        settings = SystemSettings.query.filter_by(library_id=library.id).first()
        
        # Calculate total slots per day
        total_slots = 0
        if settings:
            hours = settings.closing_time.hour - settings.opening_time.hour
            total_slots = (hours * 60) // settings.slot_duration
        
        return render_template(
            'dashboard.html',
            total_seats=total_seats,
            available_seats=available_seats,
            my_bookings=my_bookings,
            total_slots=total_slots,
            settings=settings
        )
    
    @app.route('/<slug>/seats', methods=['GET'])
    @login_required
    @approval_required
    @library_context_required
    def seats(slug):
        """Seat selection page with visual map"""
        library = g.current_library
        
        # Get date and time slot from query params or use defaults
        selected_date_str = request.args.get('date', date.today().isoformat())
        selected_time_str = request.args.get('time_slot', '')
        
        try:
            selected_date = datetime.fromisoformat(selected_date_str).date()
        except:
            selected_date = date.today()
        
        # Get system settings
        settings = SystemSettings.query.filter_by(library_id=library.id).first()
        if not settings:
            flash('Library settings not configured', 'error')
            return redirect(url_for('dashboard', slug=slug))
        
        # Generate time slots
        time_slots = generate_time_slots(
            settings.opening_time,
            settings.closing_time,
            settings.slot_duration
        )
        
        # Set selected time slot
        selected_time = None
        if selected_time_str:
            try:
                selected_time = datetime.strptime(selected_time_str, '%H:%M:%S').time()
            except:
                pass
        
        if not selected_time and time_slots:
            selected_time = time_slots[0]
        
        # Get all seats for this library
        all_seats = Seat.query.filter_by(library_id=library.id).order_by(
            Seat.number.cast(db.Integer)
        ).all()
        
        # Get bookings for selected date and time
        booked_seat_ids = []
        if selected_time:
            bookings = Booking.query.filter_by(
                library_id=library.id,
                date=selected_date,
                time_slot=selected_time,
                status=BookingStatus.booked
            ).all()
            booked_seat_ids = [b.seat_id for b in bookings]
        
        # Build seat status map
        seats_data = []
        for seat in all_seats:
            status = 'maintenance' if seat.in_maintenance else (
                'booked' if seat.id in booked_seat_ids else 'available'
            )
            seats_data.append({
                'id': seat.id,
                'number': seat.number,
                'category': seat.category.value,
                'status': status,
                'in_maintenance': seat.in_maintenance
            })
        
        return render_template(
            'seats.html',
            seats=seats_data,
            selected_date=selected_date,
            selected_time=selected_time,
            time_slots=time_slots,
            settings=settings,
            today=date.today()
        )
    
    @app.route('/<slug>/book', methods=['POST'])
    @login_required
    @approval_required
    @library_context_required
    def book_seat(slug):
        """Create a new booking"""
        library = g.current_library
        
        # Get form data
        seat_id = request.form.get('seat_id', type=int)
        booking_date_str = request.form.get('date')
        time_slot_str = request.form.get('time_slot')
        
        # Validate inputs
        if not all([seat_id, booking_date_str, time_slot_str]):
            flash('All fields are required', 'error')
            return redirect(url_for('seats', slug=slug))
        
        try:
            booking_date = datetime.fromisoformat(booking_date_str).date()
            booking_time = datetime.strptime(time_slot_str, '%H:%M:%S').time()
        except:
            flash('Invalid date or time format', 'error')
            return redirect(url_for('seats', slug=slug))
        
        # Check if date is in the past
        if booking_date < date.today():
            flash('Cannot book seats for past dates', 'error')
            return redirect(url_for('seats', slug=slug, date=booking_date_str, time_slot=time_slot_str))
        
        # Get seat
        seat = Seat.query.filter_by(id=seat_id, library_id=library.id).first()
        if not seat:
            flash('Invalid seat selected', 'error')
            return redirect(url_for('seats', slug=slug))
        
        # Check if seat is in maintenance
        if seat.in_maintenance:
            flash('This seat is currently under maintenance', 'error')
            return redirect(url_for('seats', slug=slug, date=booking_date_str, time_slot=time_slot_str))
        
        # Check role-based seat restrictions
        from models import UserRole
        
        # Researcher seats - only for researchers
        if seat.category == SeatCategory.researcher:
            if not hasattr(current_user, 'user_role') or current_user.user_role != UserRole.researcher:
                if not current_user.is_csr_super_admin:
                    flash('🔬 This seat is reserved for researchers only', 'error')
                    return redirect(url_for('seats', slug=slug, date=booking_date_str, time_slot=time_slot_str))
        
        # Staff seats - only for staff
        if seat.category == SeatCategory.staff:
            if not hasattr(current_user, 'user_role') or current_user.user_role != UserRole.staff:
                if not current_user.is_csr_super_admin:
                    flash('👔 This seat is reserved for staff only', 'error')
                    return redirect(url_for('seats', slug=slug, date=booking_date_str, time_slot=time_slot_str))
        
        # Check if seat is already booked for this slot
        existing_booking = Booking.query.filter_by(
            seat_id=seat_id,
            date=booking_date,
            time_slot=booking_time,
            status=BookingStatus.booked
        ).first()
        
        if existing_booking:
            flash('This seat is already booked for the selected time slot', 'error')
            return redirect(url_for('seats', slug=slug, date=booking_date_str, time_slot=time_slot_str))
        
        # Check if user already has a booking for this time slot
        user_existing_booking = Booking.query.filter_by(
            user_id=current_user.id,
            library_id=library.id,
            date=booking_date,
            time_slot=booking_time,
            status=BookingStatus.booked
        ).first()
        
        if user_existing_booking:
            flash('You already have a booking for this time slot', 'error')
            return redirect(url_for('seats', slug=slug, date=booking_date_str, time_slot=time_slot_str))
        
        # Create booking
        booking = Booking(
            library_id=library.id,
            user_id=current_user.id,
            seat_id=seat_id,
            date=booking_date,
            time_slot=booking_time,
            status=BookingStatus.booked
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Send confirmation email
        try:
            from services.email_service import EmailService
            EmailService.send_booking_confirmation(booking)
            flash(f'Successfully booked Seat {seat.number} for {booking_date} at {booking_time.strftime("%I:%M %p")}. Confirmation email sent!', 'success')
        except Exception as e:
            print(f"Email error: {e}")
            flash(f'Successfully booked Seat {seat.number} for {booking_date} at {booking_time.strftime("%I:%M %p")}', 'success')
        
        return redirect(url_for('my_bookings', slug=slug))
    
    @app.route('/<slug>/bookings')
    @login_required
    @approval_required
    @library_context_required
    def my_bookings(slug):
        """User's bookings for this library"""
        library = g.current_library
        
        # Get all bookings for this user and library
        bookings = Booking.query.filter_by(
            user_id=current_user.id,
            library_id=library.id
        ).order_by(Booking.date.desc(), Booking.time_slot.desc()).all()
        
        # Separate into upcoming and past
        upcoming_bookings = []
        past_bookings = []
        
        for booking in bookings:
            if booking.status == BookingStatus.booked and booking.date >= date.today():
                upcoming_bookings.append(booking)
            else:
                past_bookings.append(booking)
        
        return render_template(
            'my_bookings.html',
            upcoming_bookings=upcoming_bookings,
            past_bookings=past_bookings
        )
    
    @app.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
    @login_required
    def cancel_booking(booking_id):
        """Cancel a booking"""
        booking = Booking.query.get_or_404(booking_id)
        
        # Check if booking belongs to current user
        if booking.user_id != current_user.id:
            flash('You can only cancel your own bookings', 'error')
            return redirect(url_for('index'))
        
        # Check if booking is already cancelled or completed
        if booking.status != BookingStatus.booked:
            flash('This booking cannot be cancelled', 'error')
            return redirect(url_for('my_bookings', slug=booking.library.slug))
        
        # Check if booking is in the past
        if booking.date < date.today():
            flash('Cannot cancel past bookings', 'error')
            return redirect(url_for('my_bookings', slug=booking.library.slug))
        
        # Send cancellation email before cancelling
        try:
            from services.email_service import EmailService
            EmailService.send_cancellation_email(booking)
        except Exception as e:
            print(f"Email error: {e}")
        
        # Cancel booking
        booking.status = BookingStatus.cancelled
        db.session.commit()
        
        flash(f'Booking for Seat {booking.seat.number} on {booking.date} has been cancelled. Confirmation email sent.', 'success')
        return redirect(url_for('my_bookings', slug=booking.library.slug))
    
    # ============= Public Library Routes =============
    
    @app.route('/libraries/<slug>')
    def library_detail(slug):
        """Library detail page (public)"""
        library = Library.query.filter_by(slug=slug).first()
        if not library:
            abort(404)
        
        # Get library statistics
        total_seats = Seat.query.filter_by(library_id=library.id).count()
        general_seats = Seat.query.filter_by(library_id=library.id, category=SeatCategory.general).count()
        reserved_seats = Seat.query.filter_by(library_id=library.id, category=SeatCategory.reserved).count()
        maintenance_seats = Seat.query.filter_by(library_id=library.id, in_maintenance=True).count()
        
        # Get system settings
        settings = SystemSettings.query.filter_by(library_id=library.id).first()
        
        # Check if library has its own logo
        library_logo_url = f'/{library.logo_path}' if library.logo_path else None
        
        return render_template(
            'library_detail.html',
            library=library,
            library_logo_url=library_logo_url,
            total_seats=total_seats,
            general_seats=general_seats,
            reserved_seats=reserved_seats,
            maintenance_seats=maintenance_seats,
            settings=settings
        )
    
    # ============= Utility Routes =============
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return {'status': 'healthy', 'database': 'connected'}, 200
    
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """Serve static files"""
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        return send_from_directory(static_dir, filename)
    
    @app.route('/gallery')
    def public_gallery():
        """Public photo gallery"""
        from models import GalleryImage, GalleryStatus
        
        # Get filter params
        library_id = request.args.get('library', type=int)
        
        # Base query - only approved images
        query = GalleryImage.query.filter_by(status=GalleryStatus.approved)
        
        # Filter by library if specified
        if library_id:
            query = query.filter_by(library_id=library_id)
        
        approved_images = query.order_by(GalleryImage.uploaded_at.desc()).all()
        
        # Get all libraries for filter dropdown
        libraries = Library.query.all()
        
        return render_template(
            'public_gallery.html',
            images=approved_images,
            libraries=libraries,
            selected_library=library_id
        )
    
    # ============= AUTO-CANCELLATION SCHEDULER =============
    
    # Setup background scheduler for auto-cancellation
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    
    def auto_cancel_no_shows():
        """Background job to auto-cancel bookings where users didn't report"""
        with app.app_context():
            try:
                from services.reporting_service import ReportingService
                count = ReportingService.auto_cancel_expired_bookings()
                if count > 0:
                    print(f"🔄 Auto-cancelled {count} no-show booking(s)")
            except Exception as e:
                print(f"⚠️ Auto-cancel error: {e}")
    
    # Schedule to run every 5 minutes
    scheduler.add_job(
        func=auto_cancel_no_shows,
        trigger="interval",
        minutes=5,
        id='auto_cancel_job',
        replace_existing=True
    )
    
    scheduler.start()
    print("✓ Auto-cancellation scheduler started (runs every 5 minutes)")
    
    # Shutdown scheduler on app exit
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("🚀 Kaluwala CSR Libraries Network")
    print("   Complete System with CSR Admin Panel")
    print("="*60)
    print("📍 Server: http://localhost:5000")
    print("💾 Database: instance/kaluwala.db")
    print("⚙️  Environment: Development")
    print("\n🔐 Credentials:")
    print("   CSR Admin: admin | admin123")
    print("   Student: student1 | password123")
    print("\n🌐 CSR Admin Panel:")
    print("   http://localhost:5000/csr-admin")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
