# ADD THIS TO YOUR app.py

# ====================
# Step 1: Add import at the top
# ====================
from admin import admin_bp

# ====================
# Step 2: Register blueprint in create_app()
# ====================
def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # ... (existing instance/static folder creation)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # ⭐ ADD THIS LINE ⭐
    app.register_blueprint(admin_bp)
    
    # ... (rest of your existing code)

# ====================
# Step 3: Make sure models.py is updated
# ====================
# Replace models.py with models_admin.py (renamed to models.py)
# This adds the is_csr_super_admin field

# ====================
# Step 4: Update database and set admin as super admin
# ====================
# Run these commands:

# python
# >>> from models import db, User
# >>> from app import create_app
# >>> app = create_app()
# >>> with app.app_context():
# ...     db.drop_all()
# ...     db.create_all()
# >>> exit()

# Then run migrate.py to recreate data
# Then run this to make admin a super admin:

# python
# >>> from models import db, User
# >>> from app import create_app
# >>> app = create_app()
# >>> with app.app_context():
# ...     admin = User.query.filter_by(username='admin').first()
# ...     admin.is_csr_super_admin = True
# ...     db.session.commit()
# ...     print("Done!")
# >>> exit()

# ====================
# Step 5: Update base.html navbar
# ====================
# Add this to the navbar in base.html after the bookings link:

"""
{% if current_library and current_user.is_admin_of(current_library.id) %}
<a href="/admin/{{ current_library.slug }}" style="color: #fbbf24; font-weight: 700;">
    ⚡ Admin Panel
</a>
{% endif %}
"""

# ====================
# Complete! Test by visiting:
# ====================
# http://localhost:5000/admin/bpsmv
