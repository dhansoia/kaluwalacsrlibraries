# 🛠️ Role-Based Admin Dashboards Setup Guide

## Overview

This update adds comprehensive admin features:
- ✅ Library admin dashboard with statistics
- ✅ Seat maintenance management
- ✅ Library settings editor
- ✅ Reports and analytics
- ✅ User management
- ✅ CSR Super Admin role
- ✅ @library_admin_required decorator

## 📦 Files to Download

### Core Files
1. **models_admin.py** → Replace `models.py`
2. **admin.py** → NEW (admin blueprint)
3. **app_with_admin.py** → Replace `app.py`

### Templates
4. **admin_dashboard.html** → `templates/admin_dashboard.html`
5. **admin_seats.html** → `templates/admin_seats.html`
6. **admin_settings.html** → `templates/admin_settings.html`
7. **admin_reports.html** → `templates/admin_reports.html` (create from guide)
8. **admin_users.html** → `templates/admin_users.html` (create from guide)
9. **admin_bookings.html** → `templates/admin_bookings.html` (create from guide)

## 🚀 Installation Steps

### Step 1: Update Database Schema
```powershell
# Backup database
copy instance\kaluwala.db instance\kaluwala.db.backup

# Delete and recreate with new schema
del instance\kaluwala.db
python migrate.py
```

### Step 2: Make Admin a CSR Super Admin
```powershell
# After migration, update admin user
python
>>> from models import db, User
>>> from app import create_app
>>> app = create_app()
>>> with app.app_context():
...     admin = User.query.filter_by(username='admin').first()
...     admin.is_csr_super_admin = True
...     db.session.commit()
...     print("Admin is now CSR Super Admin")
>>> exit()
```

### Step 3: Add Admin Blueprint to app.py

Add these lines to your app.py:

```python
# At the top with other imports:
from admin import admin_bp

# In create_app(), after db.init_app(app):
app.register_blueprint(admin_bp)
```

Full integration example:
```python
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Register admin blueprint
    from admin import admin_bp
    app.register_blueprint(admin_bp)
    
    # ... rest of your code
```

### Step 4: Update Base Template Navigation

Add admin link to navbar in `base.html`:

```html
{% if current_user.is_authenticated %}
<nav class="navbar">
    <div class="navbar-menu">
        {% if current_library %}
        <a href="/{{ current_library.slug }}/dashboard">Dashboard</a>
        <a href="/{{ current_library.slug }}/bookings">My Bookings</a>
        
        <!-- Add this admin check -->
        {% if current_user.is_admin_of(current_library.id) %}
        <a href="/admin/{{ current_library.slug }}" style="color: #fbbf24;">⚡ Admin</a>
        {% endif %}
        
        {% endif %}
        <a href="/switch-library">Switch Library</a>
        <span style="color: #666;">{{ current_user.username }}</span>
        <a href="/logout" class="logout-btn">Logout</a>
    </div>
</nav>
{% endif %}
```

## ✨ New Features

### 1. Admin Dashboard (`/admin/<slug>`)

**Statistics Cards**:
- Total Seats
- Seats in Maintenance
- Today's Bookings
- Month's Bookings
- Active Users

**Features**:
- Recent bookings table
- Quick action buttons
- Navigation tabs
- Real-time stats

### 2. Manage Seats (`/admin/<slug>/seats`)

**Features**:
- View all seats
- Toggle maintenance status
- See booking count per seat
- Color-coded status (green=available, red=maintenance)

**Actions**:
- Click "Set Maintenance" to disable seat
- Click "Mark Available" to enable seat
- Changes take effect immediately

### 3. Library Settings (`/admin/<slug>/settings`)

**Configurable Settings**:
- Opening Time (e.g., 09:00)
- Closing Time (e.g., 21:00)
- Slot Duration (15-240 minutes)
- Login Marquee Message
- Maintenance Mode (disable all bookings)

**Validation**:
- Opening < Closing time
- Slot duration 15-240 min
- All fields required

### 4. Reports & Analytics (`/admin/<slug>/reports`)

**Metrics**:
- Total bookings in period
- Bookings by status (booked/cancelled/completed)
- Daily booking trends (chart)
- Seat utilization (top 10)
- Peak hours analysis
- Top users (most bookings)

**Features**:
- Date range filter (7/30/90 days)
- Visual charts with Chart.js
- Export capability (future)

### 5. Manage Users (`/admin/<slug>/users`)

**Features**:
- View all users with bookings
- See staff assignments
- User statistics
- (Future: Add/remove staff)

### 6. All Bookings (`/admin/<slug>/bookings`)

**Features**:
- View all library bookings
- Filter by status
- Filter by date
- Cancel any booking
- Paginated results (100 per page)

## 🔐 Access Control

### CSR Super Admin
- Has admin access to ALL libraries
- Set via `is_csr_super_admin = True`
- Can manage any library

### Library Admin
- Has admin access to assigned libraries
- Set via LibraryAdmin table with role='admin'
- Can only manage assigned libraries

### Library Staff
- Has staff access to assigned libraries
- Set via LibraryAdmin table with role='staff'
- Limited permissions (future implementation)

### Regular User
- No admin access
- Can only book and manage own bookings

## 🧪 Testing Guide

### Test 1: Access Admin Dashboard
1. Login as admin (CSR Super Admin)
2. Go to BPSMV dashboard
3. Look for "⚡ Admin" link in navbar
4. Click it

**Expected**:
- ✅ Redirects to `/admin/bpsmv`
- ✅ Shows admin dashboard
- ✅ Statistics display correctly
- ✅ Recent bookings table populated

### Test 2: Toggle Seat Maintenance
1. From admin dashboard, click "Manage Seats"
2. Find any available seat
3. Click "🔧 Set Maintenance"

**Expected**:
- ✅ Seat turns red
- ✅ Success message appears
- ✅ Button changes to "✓ Mark Available"
- ✅ Seat no longer bookable by users

### Test 3: Update Library Settings
1. From admin dashboard, click "Settings"
2. Change opening time to 08:00
3. Change closing time to 22:00
4. Change slot duration to 30
5. Update marquee message
6. Click "Save Settings"

**Expected**:
- ✅ Success message appears
- ✅ Settings saved in database
- ✅ New time slots appear on booking page
- ✅ Marquee updates on dashboard

### Test 4: View Reports
1. From admin dashboard, click "Reports"
2. Select "Last 30 Days"
3. View charts and statistics

**Expected**:
- ✅ Shows total bookings
- ✅ Status breakdown chart
- ✅ Daily bookings line chart
- ✅ Seat utilization data
- ✅ Peak hours analysis
- ✅ Top users list

### Test 5: Cancel User Booking (Admin)
1. Go to "All Bookings"
2. Find an active booking
3. Click cancel button
4. Confirm

**Expected**:
- ✅ Booking status changes to cancelled
- ✅ Seat becomes available
- ✅ Success message shown
- ✅ User sees booking as cancelled

### Test 6: Non-Admin Access
1. Logout admin
2. Login as student1
3. Try to access `/admin/bpsmv`

**Expected**:
- ✅ Redirected to regular dashboard
- ✅ Error message: "No admin access"
- ✅ No admin link in navbar

### Test 7: CSR Super Admin Powers
1. Login as admin (CSR Super Admin)
2. Create a second library via database
3. Try to access its admin panel

**Expected**:
- ✅ Can access any library's admin
- ✅ No LibraryAdmin record needed
- ✅ Full admin permissions everywhere

## 📊 Database Changes

### New Field in User Table
```sql
ALTER TABLE user ADD COLUMN is_csr_super_admin BOOLEAN DEFAULT 0;
```

### Set Admin as Super Admin
```sql
UPDATE user SET is_csr_super_admin = 1 WHERE username = 'admin';
```

### Verify
```sql
SELECT username, is_csr_super_admin FROM user;
```

## 🎨 UI Features

### Admin Badge
- Yellow badge showing "ADMIN" in navbar
- Gold "⚡ Admin" link
- Distinct admin header styling

### Color Coding
- **Green**: Available/Active
- **Red**: Maintenance/Cancelled
- **Yellow**: Warning/Admin
- **Gray**: Disabled

### Responsive Design
- Mobile-friendly tables
- Adaptive grid layouts
- Scrollable tabs on mobile

## 🔧 Code Structure

### Admin Routes
```
GET  /admin/<slug>                         # Dashboard
GET  /admin/<slug>/seats                   # Manage seats
POST /admin/<slug>/seats/<id>/toggle       # Toggle maintenance
GET  /admin/<slug>/settings                # View settings
POST /admin/<slug>/settings                # Update settings
GET  /admin/<slug>/reports                 # View reports
GET  /admin/<slug>/users                   # Manage users
GET  /admin/<slug>/bookings                # All bookings
POST /admin/<slug>/bookings/<id>/cancel    # Cancel booking
GET  /admin/<slug>/api/stats               # Stats API
```

### Decorator Usage
```python
@admin_bp.route('/<slug>')
@library_admin_required
def dashboard(slug):
    library = g.admin_library  # Set by decorator
    # ... admin code
```

### Permission Check
```python
# In template
{% if current_user.is_admin_of(library.id) %}
    <a href="/admin/{{ library.slug }}">Admin</a>
{% endif %}

# In view
if not current_user.is_admin_of(library.id):
    flash('Access denied', 'error')
    return redirect(url_for('index'))
```

## 📈 Reports Template (Create This)

Create `templates/admin_reports.html`:

```html
{% extends "base.html" %}
{% block content %}
<div style="max-width: 1400px; margin: 0 auto;">
    <h1>📈 Reports & Analytics</h1>
    
    <!-- Period Selector -->
    <select onchange="window.location.href='?days='+this.value">
        <option value="7" {% if days==7 %}selected{% endif %}>Last 7 Days</option>
        <option value="30" {% if days==30 %}selected{% endif %}>Last 30 Days</option>
        <option value="90" {% if days==90 %}selected{% endif %}>Last 90 Days</option>
    </select>
    
    <!-- Total Bookings -->
    <h2>Total: {{ total_bookings }}</h2>
    
    <!-- Daily Chart -->
    <canvas id="dailyChart"></canvas>
    
    <!-- Seat Utilization -->
    <h2>Top Seats</h2>
    {% for seat, count in seat_utilization %}
        <div>Seat {{ seat }}: {{ count }} bookings</div>
    {% endfor %}
    
    <!-- Peak Hours -->
    <h2>Peak Hours</h2>
    {% for hour, count in peak_hours %}
        <div>{{ hour }}:00 - {{ count }} bookings</div>
    {% endfor %}
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx = document.getElementById('dailyChart');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: {{ daily_bookings|map(attribute=0)|list|tojson }},
        datasets: [{
            label: 'Bookings',
            data: {{ daily_bookings|map(attribute=1)|list|tojson }},
            borderColor: '#4a7c2c',
            tension: 0.1
        }]
    }
});
</script>
{% endblock %}
```

## ✅ Success Criteria

Admin system is working when:
- [ ] CSR Super Admin can access `/admin/bpsmv`
- [ ] Admin dashboard shows correct statistics
- [ ] Can toggle seat maintenance
- [ ] Settings update successfully
- [ ] Reports display data
- [ ] Can view all bookings
- [ ] Can cancel any booking
- [ ] Non-admins see "Access denied"
- [ ] Admin link appears in navbar
- [ ] All tabs navigate correctly

## 🎯 Next Steps

After admin system is working:

### Phase 1: Enhanced Admin
- [ ] Add/remove staff members
- [ ] Bulk seat operations
- [ ] Export reports to CSV
- [ ] Email notifications to users

### Phase 2: Super Admin Panel
- [ ] Manage all libraries
- [ ] Create new libraries
- [ ] System-wide statistics
- [ ] User management across libraries

### Phase 3: Advanced Features
- [ ] Audit logs
- [ ] Backup/restore
- [ ] Custom roles
- [ ] API access

## 🐛 Troubleshooting

**Issue**: No admin link in navbar
**Solution**: Check `current_user.is_admin_of(current_library.id)` returns True

**Issue**: "Access denied" for admin user
**Solution**: Verify CSR Super Admin flag or LibraryAdmin record exists

**Issue**: Statistics show 0
**Solution**: Create some test bookings first

**Issue**: Settings won't save
**Solution**: Check time format (HH:MM) and validation

**Issue**: Charts don't display
**Solution**: Include Chart.js CDN in template

## 🎉 Features Summary

**Admin Dashboard**:
- Real-time statistics
- Recent activity
- Quick actions
- Tab navigation

**Seat Management**:
- One-click maintenance toggle
- Booking count per seat
- Visual status indicators
- Bulk operations (future)

**Settings**:
- Operating hours
- Slot duration
- Marquee message
- Maintenance mode

**Reports**:
- Daily trends
- Seat utilization
- Peak hours
- Top users
- Exportable data

**Access Control**:
- CSR Super Admin (all libraries)
- Library Admin (assigned libraries)
- Decorator-based protection
- Clear permission model

Ready to manage your libraries! 🚀
