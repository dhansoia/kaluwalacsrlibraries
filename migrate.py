"""
Database Migration and Seeding Script
Creates initial data for Kaluwala CSR Libraries Network
Includes BPSMV Central Library setup with official logo
"""

import os
import sys
from datetime import time
from flask import Flask
from config import config
from models import db, User, Library, Seat, SystemSettings, LibraryAdmin, SeatCategory, AdminRole

def create_app():
    """Create Flask app for migration"""
    app = Flask(__name__)
    app.config.from_object(config['development'])
    
    # Ensure instance folder exists
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    db.init_app(app)
    return app

def create_bpsmv_library():
    """Create BPSMV Central Library"""
    print("\n📚 Creating BPSMV Central Library...")
    
    # Check if library already exists
    existing = Library.query.filter_by(slug='bpsmv').first()
    if existing:
        print("⚠️  BPSMV Library already exists. Skipping...")
        return existing
    
    library = Library(
        name='BPS Mahila Vishwavidyalaya Library',
        slug='bpsmv',
        address='Khanpur Kalan, Sonipat',
        city='Sonipat',
        state='Haryana',
        pincode='131305',
        logo_path='static/bpsmv_logo.png',  # BPSMV logo
        contact_email='library@bpsmv.ac.in',
        contact_phone='+91-130-2228910',
        csr_partner='Kaluwala Constructions Pvt Ltd'
    )
    
    db.session.add(library)
    db.session.commit()
    print(f"✓ Created library: {library.name} (ID: {library.id})")
    print(f"  Logo: {library.logo_path}")
    return library

def create_seats(library):
    """Create 60 seats for the library with mixed categories"""
    print(f"\n💺 Creating seats for {library.name}...")
    
    # Check if seats already exist
    existing_count = Seat.query.filter_by(library_id=library.id).count()
    if existing_count > 0:
        print(f"⚠️  {existing_count} seats already exist. Skipping...")
        return
    
    seats_created = 0
    
    # Create 60 seats with mixed categories
    # First 45 seats: General (75%)
    # Last 15 seats: Reserved (25%)
    for i in range(1, 61):
        category = SeatCategory.reserved if i > 45 else SeatCategory.general
        
        seat = Seat(
            library_id=library.id,
            number=str(i),
            category=category,
            in_maintenance=False
        )
        db.session.add(seat)
        seats_created += 1
    
    db.session.commit()
    print(f"✓ Created {seats_created} seats")
    print(f"  - General seats: 45 (Seats 1-45)")
    print(f"  - Reserved seats: 15 (Seats 46-60)")

def create_system_settings(library):
    """Create default system settings for the library"""
    print(f"\n⚙️  Creating system settings for {library.name}...")
    
    # Check if settings already exist
    existing = SystemSettings.query.filter_by(library_id=library.id).first()
    if existing:
        print("⚠️  System settings already exist. Skipping...")
        return existing
    
    settings = SystemSettings(
        library_id=library.id,
        opening_time=time(9, 0),   # 9:00 AM
        closing_time=time(21, 0),  # 9:00 PM
        slot_duration=60,          # 60 minutes
        login_marquee='Welcome to BPS Mahila Vishwavidyalaya Library - Empowering Women with Education - Powered by Kaluwala Constructions',
        maintenance_mode=False
    )
    
    db.session.add(settings)
    db.session.commit()
    print(f"✓ Created system settings")
    print(f"  - Opening time: 9:00 AM")
    print(f"  - Closing time: 9:00 PM")
    print(f"  - Slot duration: 60 minutes")
    print(f"  - Total slots per day: 12")
    return settings

def create_admin_user(library):
    """Create default admin user for the library"""
    print(f"\n👤 Creating admin user for {library.name}...")
    
    # Check if admin user already exists
    existing_user = User.query.filter_by(username='admin').first()
    if existing_user:
        print(f"⚠️  User 'admin' already exists (ID: {existing_user.id})")
        
        # Check if already assigned to this library
        existing_assignment = LibraryAdmin.query.filter_by(
            user_id=existing_user.id,
            library_id=library.id
        ).first()
        
        if existing_assignment:
            print(f"⚠️  Admin already assigned to {library.name}. Skipping...")
            return existing_user
        else:
            # Assign existing admin to this library
            assignment = LibraryAdmin(
                user_id=existing_user.id,
                library_id=library.id,
                role=AdminRole.admin
            )
            db.session.add(assignment)
            db.session.commit()
            print(f"✓ Assigned existing admin to {library.name}")
            return existing_user
    
    # Create new admin user
    admin = User(
        username='admin',
        email='admin@bpsmv.ac.in'
    )
    admin.set_password('admin123')
    
    db.session.add(admin)
    db.session.commit()
    print(f"✓ Created admin user")
    print(f"  - Username: admin")
    print(f"  - Email: admin@bpsmv.ac.in")
    print(f"  - Password: admin123")
    print(f"  - User ID: {admin.id}")
    
    # Assign admin role to BPSMV library
    assignment = LibraryAdmin(
        user_id=admin.id,
        library_id=library.id,
        role=AdminRole.admin
    )
    db.session.add(assignment)
    db.session.commit()
    print(f"✓ Assigned admin role for {library.name}")
    
    return admin

def run_migration():
    """Run the complete migration"""
    print("="*70)
    print("🚀 Kaluwala CSR Libraries - Database Migration")
    print("   BPS Mahila Vishwavidyalaya, Sonipat")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("\n📊 Creating database tables...")
        db.create_all()
        print("✓ Database tables ready")
        
        # Create BPSMV library
        library = create_bpsmv_library()
        
        # Create seats
        create_seats(library)
        
        # Create system settings
        create_system_settings(library)
        
        # Create admin user
        create_admin_user(library)
        
        # Summary
        print("\n" + "="*70)
        print("✅ Migration Complete!")
        print("="*70)
        print("\n📋 Summary:")
        print(f"  Libraries: {Library.query.count()}")
        print(f"  Seats: {Seat.query.count()}")
        print(f"  Users: {User.query.count()}")
        print(f"  System Settings: {SystemSettings.query.count()}")
        print(f"  Library Admins: {LibraryAdmin.query.count()}")
        
        print("\n🎓 BPSMV Library Details:")
        print(f"  Name: {library.name}")
        print(f"  Location: {library.address}, {library.city}")
        print(f"  Logo: {library.logo_path}")
        print(f"  CSR Partner: {library.csr_partner}")
        
        print("\n🔑 Admin Credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Email: admin@bpsmv.ac.in")
        
        print("\n🌐 Test URLs:")
        print("  Main: http://localhost:5000")
        print("  BPSMV: http://localhost:5000/libraries/bpsmv")
        print("  Health: http://localhost:5000/health")
        
        print("\n💡 Next steps:")
        print("  1. Make sure bpsmv_logo.png is in the static/ folder")
        print("  2. Run: python app.py")
        print("  3. Visit: http://localhost:5000/libraries/bpsmv")
        print("  4. Start building authentication features")
        print("="*70 + "\n")

if __name__ == '__main__':
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
