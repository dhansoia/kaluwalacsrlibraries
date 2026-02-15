# 🚀 COMPLETE SETUP GUIDE - Advanced Features
## Email, PDF Reports, and Bulk Operations

## 📦 Files Included

You have received:
1. ✅ services/email_service.py
2. ✅ services/pdf_service.py
3. ✅ services/bulk_service.py
4. ✅ services/__init__.py
5. ✅ config.py
6. ✅ .env.example
7. ✅ requirements.txt
8. ✅ templates/admin_bulk_operations.html

## 🔧 STEP-BY-STEP INSTALLATION

### Step 1: Install Dependencies

```powershell
# Install all required packages
pip install -r requirements.txt
```

### Step 2: Setup Environment Variables

```powershell
# Copy the example file
copy .env.example .env

# Edit .env file and fill in your details
notepad .env
```

**For Gmail Setup:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to https://myaccount.google.com/apppasswords
4. Select "Mail" and "Windows Computer"
5. Copy the 16-character password
6. Paste in .env file as MAIL_PASSWORD

### Step 3: Create Services Folder

```powershell
# Create services directory
mkdir services

# Copy all service files to services/
# - email_service.py
# - pdf_service.py
# - bulk_service.py
# - __init__.py
```

### Step 4: Update app.py

Add at the top of app.py (after imports):

```python
from flask_mail import Mail
from config import Config

# Initialize Mail
mail = Mail()
```

In create_app() function, add after db.init_app(app):

```python
def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)  # ADD THIS LINE
    migrate.init_app(app, db)
    
    # ... rest of code
```

Add email notifications to book_seat() function:

```python
@app.route('/<slug>/book', methods=['POST'])
@login_required
@approval_required
@library_context_required
def book_seat(slug):
    # ... existing validation code ...
    
    # Create booking
    booking = Booking(...)
    db.session.add(booking)
    db.session.commit()
    
    # ADD THESE LINES:
    # Send confirmation email
    try:
        from services.email_service import EmailService
        EmailService.send_booking_confirmation(booking)
        flash('Booking confirmed! Confirmation email sent.', 'success')
    except Exception as e:
        flash('Booking confirmed! (Email notification failed)', 'success')
    
    return redirect(url_for('my_bookings', slug=slug))
```

Add email to cancel_booking() function:

```python
@app.route('/<slug>/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
@library_context_required
def cancel_booking(slug, booking_id):
    # ... existing validation ...
    
    # ADD BEFORE CANCELLATION:
    try:
        from services.email_service import EmailService
        EmailService.send_cancellation_email(booking)
    except:
        pass
    
    booking.status = BookingStatus.cancelled
    db.session.commit()
    
    # ... rest of code
```

### Step 5: Update admin.py

Add imports at top:

```python
from flask import send_file
from datetime import timedelta
from services.bulk_service import BulkOperationsService
from services.pdf_service import PDFReportService
```

Add these routes at the end of admin.py:

```python
# ============= PDF REPORTS =============

@admin_bp.route('/<slug>/reports/pdf', methods=['GET'])
@library_admin_required
def download_pdf_report(slug):
    """Generate and download PDF report"""
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
    library = g.admin_library
    
    start = int(request.form.get('start_number'))
    end = int(request.form.get('end_number'))
    category_str = request.form.get('category')
    
    from models import SeatCategory
    category = SeatCategory[category_str]
    
    created, errors = BulkOperationsService.bulk_create_seats(
        library.id, start, end, category
    )
    
    if errors:
        flash(f'Created {len(created)} seats. Errors: {len(errors)}', 'warning')
    else:
        flash(f'Successfully created {len(created)} seats!', 'success')
    
    return redirect(url_for('admin.bulk_operations', slug=slug))

@admin_bp.route('/<slug>/bulk/update-category', methods=['POST'])
@library_admin_required
def bulk_update_category(slug):
    library = g.admin_library
    
    seat_numbers_str = request.form.get('seat_numbers')
    seat_numbers = [n.strip() for n in seat_numbers_str.split(',')]
    category_str = request.form.get('category')
    
    from models import SeatCategory
    category = SeatCategory[category_str]
    
    updated, errors = BulkOperationsService.bulk_update_seat_category(
        library.id, seat_numbers, category
    )
    
    flash(f'Updated {len(updated)} seats to {category_str}!', 'success')
    return redirect(url_for('admin.bulk_operations', slug=slug))

@admin_bp.route('/<slug>/bulk/toggle-maintenance', methods=['POST'])
@library_admin_required
def bulk_toggle_maintenance(slug):
    library = g.admin_library
    
    seat_numbers_str = request.form.get('seat_numbers')
    seat_numbers = [n.strip() for n in seat_numbers_str.split(',')]
    maintenance = request.form.get('maintenance') == 'true'
    
    updated, errors = BulkOperationsService.bulk_toggle_maintenance(
        library.id, seat_numbers, maintenance
    )
    
    status = 'enabled' if maintenance else 'disabled'
    flash(f'Maintenance {status} for {len(updated)} seats!', 'success')
    return redirect(url_for('admin.bulk_operations', slug=slug))

@admin_bp.route('/<slug>/bulk/cancel-bookings', methods=['POST'])
@library_admin_required
def bulk_cancel_bookings(slug):
    library = g.admin_library
    
    date_str = request.form.get('date')
    booking_date = datetime.fromisoformat(date_str).date()
    
    count = BulkOperationsService.bulk_cancel_bookings(
        library.id, booking_date
    )
    
    flash(f'Cancelled {count} bookings for {date_str}. Emails sent to users.', 'success')
    return redirect(url_for('admin.bulk_operations', slug=slug))
```

Add email to approve_user() function:

```python
@admin_bp.route('/<slug>/users/<int:user_id>/approve', methods=['POST'])
@library_admin_required
def approve_user(slug, user_id):
    # ... existing code ...
    
    db.session.commit()
    
    # ADD AFTER COMMIT:
    try:
        from services.email_service import EmailService
        EmailService.send_approval_email(user, library)
    except:
        pass
    
    flash(f'User {user.username} approved as {user_role}!', 'success')
    return redirect(url_for('admin.pending_users', slug=slug))
```

### Step 6: Update admin_dashboard.html

Add buttons in Quick Actions section:

```html
<a href="{{ url_for('admin.download_pdf_report', slug=library.slug) }}" class="btn btn-primary">
    📄 Download PDF Report
</a>
<a href="{{ url_for('admin.bulk_operations', slug=library.slug) }}" class="btn btn-secondary">
    ⚡ Bulk Operations
</a>
```

### Step 7: Copy Template Files

Copy admin_bulk_operations.html to templates/ folder

### Step 8: Test Email Configuration

Create test_email.py:

```python
from app import create_app, mail
from flask_mail import Message

app = create_app()

with app.app_context():
    msg = Message(
        'Test Email',
        recipients=['your-email@gmail.com'],
        html='<h1>Email works!</h1>'
    )
    mail.send(msg)
    print("Email sent successfully!")
```

Run:
```powershell
python test_email.py
```

## ✅ TESTING CHECKLIST

### Email Notifications:
1. [ ] Book a seat → Check inbox for confirmation
2. [ ] Cancel booking → Check inbox for cancellation
3. [ ] Approve user → Check inbox for approval
4. [ ] Verify email formatting looks good

### PDF Reports:
1. [ ] Click "Download PDF Report" in admin dashboard
2. [ ] Open PDF and verify data
3. [ ] Check formatting and layout

### Bulk Operations:
1. [ ] Create seats 101-110 (general category)
2. [ ] Update seats 1,2,3 to researcher category
3. [ ] Enable maintenance for seats 4,5,6
4. [ ] Test bulk cancel (use future date)

## 🎉 RESULT

After setup, you'll have:

✅ **Email Notifications:**
- Booking confirmations
- Cancellation notices
- Approval emails
- Professional HTML templates

✅ **PDF Reports:**
- Download booking reports
- Professional formatting
- Statistics and charts
- Date range selection

✅ **Bulk Operations:**
- Create 100 seats in seconds
- Update categories in bulk
- Toggle maintenance for multiple seats
- Cancel all bookings for holidays

## 🆘 TROUBLESHOOTING

**Email not sending:**
- Check Gmail App Password (16 characters)
- Verify 2-Step Verification is enabled
- Check .env file has correct values
- Look for error messages in console

**PDF not downloading:**
- Install reportlab: pip install reportlab
- Check if import errors in console
- Verify route is accessible

**Bulk operations errors:**
- Check seat numbers format (comma-separated)
- Verify seats exist in database
- Check for future bookings before delete

## 📧 Support

If you encounter issues:
1. Check console for error messages
2. Verify all packages installed
3. Ensure .env file configured
4. Test email config separately

Total setup time: 30-60 minutes
