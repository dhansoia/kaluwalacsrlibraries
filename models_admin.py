from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

# Enums for database fields
class SeatCategory(enum.Enum):
    general = 'general'
    reserved = 'reserved'

class BookingStatus(enum.Enum):
    booked = 'booked'
    cancelled = 'cancelled'
    completed = 'completed'

class AdminRole(enum.Enum):
    admin = 'admin'
    staff = 'staff'

# Association table for Library-User many-to-many relationship
class LibraryAdmin(db.Model):
    __tablename__ = 'library_admin'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey('library.id'), primary_key=True)
    role = db.Column(db.Enum(AdminRole), nullable=False, default=AdminRole.staff)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='library_assignments')
    library = db.relationship('Library', back_populates='admin_assignments')

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_csr_super_admin = db.Column(db.Boolean, default=False, nullable=False)  # NEW
    home_library_id = db.Column(db.Integer, db.ForeignKey('library.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    library_assignments = db.relationship('LibraryAdmin', back_populates='user', cascade='all, delete-orphan')
    home_library = db.relationship('Library', foreign_keys=[home_library_id])
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return str(self.id)
    
    def is_admin_of(self, library_id):
        """Check if user is admin of a specific library"""
        # CSR Super Admins have admin access to all libraries
        if self.is_csr_super_admin:
            return True
        
        assignment = LibraryAdmin.query.filter_by(
            user_id=self.id, 
            library_id=library_id,
            role=AdminRole.admin
        ).first()
        return assignment is not None
    
    def is_staff_of(self, library_id):
        """Check if user is staff or admin of a specific library"""
        # CSR Super Admins have staff access to all libraries
        if self.is_csr_super_admin:
            return True
        
        assignment = LibraryAdmin.query.filter_by(
            user_id=self.id, 
            library_id=library_id
        ).first()
        return assignment is not None
    
    def get_accessible_libraries(self):
        """Get all libraries the user has access to"""
        # CSR Super Admins can access all libraries
        if self.is_csr_super_admin:
            return Library.query.all()
        
        assignments = LibraryAdmin.query.filter_by(user_id=self.id).all()
        return [assignment.library for assignment in assignments]
    
    def __repr__(self):
        return f'<User {self.username}>'

class Library(db.Model):
    __tablename__ = 'library'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    logo_path = db.Column(db.String(255))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    csr_partner = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    seats = db.relationship('Seat', back_populates='library', lazy='dynamic', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', back_populates='library', lazy='dynamic', cascade='all, delete-orphan')
    settings = db.relationship('SystemSettings', back_populates='library', uselist=False, cascade='all, delete-orphan')
    admin_assignments = db.relationship('LibraryAdmin', back_populates='library', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Library {self.name}>'

class Seat(db.Model):
    __tablename__ = 'seat'
    
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey('library.id'), nullable=False, index=True)
    number = db.Column(db.String(20), nullable=False)
    category = db.Column(db.Enum(SeatCategory), nullable=False, default=SeatCategory.general)
    in_maintenance = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    library = db.relationship('Library', back_populates='seats')
    bookings = db.relationship('Booking', back_populates='seat', lazy='dynamic', cascade='all, delete-orphan')
    
    # Unique constraint: seat number must be unique within a library
    __table_args__ = (
        db.UniqueConstraint('library_id', 'number', name='unique_seat_per_library'),
    )
    
    def __repr__(self):
        return f'<Seat {self.number} at Library {self.library_id}>'

class Booking(db.Model):
    __tablename__ = 'booking'
    
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey('library.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    time_slot = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum(BookingStatus), nullable=False, default=BookingStatus.booked)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    library = db.relationship('Library', back_populates='bookings')
    user = db.relationship('User', back_populates='bookings')
    seat = db.relationship('Seat', back_populates='bookings')
    
    # Unique constraint: one booking per seat per date per time_slot
    __table_args__ = (
        db.UniqueConstraint('seat_id', 'date', 'time_slot', name='unique_booking_per_slot'),
        db.Index('idx_library_date', 'library_id', 'date'),
    )
    
    def __repr__(self):
        return f'<Booking {self.id} - Seat {self.seat_id} on {self.date}>'

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey('library.id'), nullable=False, unique=True, index=True)
    opening_time = db.Column(db.Time, nullable=False)
    closing_time = db.Column(db.Time, nullable=False)
    slot_duration = db.Column(db.Integer, nullable=False, default=60)  # in minutes
    login_marquee = db.Column(db.Text)
    maintenance_mode = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    library = db.relationship('Library', back_populates='settings')
    
    def __repr__(self):
        return f'<SystemSettings for Library {self.library_id}>'
