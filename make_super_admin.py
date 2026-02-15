from models import db, User
from app import create_app

app = create_app()
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    admin.is_csr_super_admin = True
    db.session.commit()
    print('✓ Admin is now CSR Super Admin!')