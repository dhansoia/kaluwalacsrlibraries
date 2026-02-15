# Verify CSR Super Admin Status
# Run this to check and fix the admin user

from models import db, User
from app import create_app

app = create_app()

with app.app_context():
    # Get admin user
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        print("❌ Admin user not found!")
        print("Run: python migrate.py")
    else:
        print(f"✓ Found admin user")
        print(f"  Username: {admin.username}")
        print(f"  Email: {admin.email}")
        print(f"  Is Active: {admin.is_active}")
        print(f"  Is CSR Super Admin: {admin.is_csr_super_admin}")
        
        if not admin.is_csr_super_admin:
            print("\n⚠️  Admin is NOT a CSR Super Admin!")
            print("Fixing now...")
            admin.is_csr_super_admin = True
            db.session.commit()
            print("✅ Admin is now CSR Super Admin!")
        else:
            print("\n✅ Admin is already CSR Super Admin!")
        
    print("\n" + "="*50)
    print("NEXT STEPS:")
    print("1. Restart your app: python app.py")
    print("2. Login as: admin / admin123")
    print("3. You should see: 🌐 CSR Admin button")
    print("="*50)
