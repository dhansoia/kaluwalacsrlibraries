"""
Seed Test Users Script
Creates test user accounts for development
"""

import os
import sys
from flask import Flask
from config import config
from models import db, User, Library

def create_app():
    """Create Flask app for seeding"""
    app = Flask(__name__)
    app.config.from_object(config['development'])
    
    # Ensure instance folder exists
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    db.init_app(app)
    return app

def seed_users():
    """Create test users"""
    print("="*60)
    print("🌱 Seeding Test Users")
    print("="*60)
    
    app = create_app()
    
    with app.app_context():
        # Get BPSMV library
        bpsmv = Library.query.filter_by(slug='bpsmv').first()
        if not bpsmv:
            print("❌ Error: BPSMV library not found. Run migrate.py first.")
            return False
        
        # Test users to create
        test_users = [
            {
                'username': 'student1',
                'email': 'student1@example.com',
                'password': 'password123',
                'home_library_id': bpsmv.id
            },
            {
                'username': 'student2',
                'email': 'student2@example.com',
                'password': 'password123',
                'home_library_id': bpsmv.id
            },
            {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'test123',
                'home_library_id': bpsmv.id
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for user_data in test_users:
            # Check if user already exists
            existing = User.query.filter_by(username=user_data['username']).first()
            if existing:
                print(f"⚠️  User '{user_data['username']}' already exists. Skipping...")
                skipped_count += 1
                continue
            
            # Create new user
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                home_library_id=user_data['home_library_id'],
                is_active=True
            )
            user.set_password(user_data['password'])
            
            db.session.add(user)
            created_count += 1
            print(f"✓ Created user: {user_data['username']}")
        
        db.session.commit()
        
        # Summary
        print("\n" + "="*60)
        print("✅ User Seeding Complete!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  Created: {created_count} users")
        print(f"  Skipped: {skipped_count} users (already exist)")
        print(f"  Total users in DB: {User.query.count()}")
        
        print("\n🔑 Test Credentials:")
        print("\n  Admin Account:")
        print("    Username: admin")
        print("    Password: admin123")
        
        print("\n  Student Accounts:")
        print("    Username: student1 | Password: password123")
        print("    Username: student2 | Password: password123")
        
        print("\n  Test Account:")
        print("    Username: testuser | Password: test123")
        
        print("\n💡 All accounts are linked to BPSMV library")
        print("\n🌐 Login at: http://localhost:5000/login")
        print("="*60 + "\n")
        
        return True

if __name__ == '__main__':
    try:
        seed_users()
    except Exception as e:
        print(f"\n❌ Seeding failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
