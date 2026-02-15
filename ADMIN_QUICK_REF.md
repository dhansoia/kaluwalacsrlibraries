# 🛠️ Admin Features - Quick Reference

## Installation (5 Steps)

```powershell
# 1. Replace models.py with models_admin.py
# 2. Add admin.py to project root
# 3. Add one line to app.py: app.register_blueprint(admin_bp)
# 4. Reset database
del instance\kaluwala.db
python migrate.py

# 5. Make admin a super admin
python
>>> from models import db, User
>>> from app import create_app
>>> app = create_app()
>>> with app.app_context():
...     admin = User.query.filter_by(username='admin').first()
...     admin.is_csr_super_admin = True
...     db.session.commit()
>>> exit()
```

## Admin Routes

| Route | Purpose |
|-------|---------|
| `/admin/bpsmv` | Admin Dashboard |
| `/admin/bpsmv/seats` | Manage Seats |
| `/admin/bpsmv/settings` | Library Settings |
| `/admin/bpsmv/reports` | Analytics & Reports |
| `/admin/bpsmv/bookings` | All Bookings |
| `/admin/bpsmv/users` | User Management |

## Access Levels

**CSR Super Admin** (`is_csr_super_admin = True`):
- ✅ Access ALL libraries
- ✅ Full admin permissions everywhere
- ✅ No LibraryAdmin record needed

**Library Admin** (LibraryAdmin with role='admin'):
- ✅ Access assigned libraries only
- ✅ Full admin permissions for assigned libraries
- ✅ Requires LibraryAdmin record

**Regular User**:
- ❌ No admin access
- ✅ Can only book and manage own bookings

## Key Features

### Dashboard Statistics
- Total Seats
- Maintenance Count
- Today's Bookings
- Monthly Bookings
- Active Users

### Seat Management
- Toggle maintenance status
- View booking counts
- Color-coded status
- One-click updates

### Settings
- Opening/Closing times
- Slot duration
- Marquee message
- Maintenance mode toggle

### Reports
- Daily booking trends
- Seat utilization
- Peak hours analysis
- Top users
- Status breakdown

## Quick Actions

**Toggle Seat Maintenance**:
```
Admin → Manage Seats → Click "Set Maintenance"
```

**Update Library Hours**:
```
Admin → Settings → Change times → Save
```

**Cancel Any Booking**:
```
Admin → All Bookings → Find booking → Cancel
```

**View Analytics**:
```
Admin → Reports → Select period → View charts
```

## Template Files

```
templates/
├── admin_dashboard.html   ✅ Main dashboard
├── admin_seats.html       ✅ Seat management
├── admin_settings.html    ✅ Settings editor
├── admin_reports.html     ⚠️  Create from guide
├── admin_bookings.html    ⚠️  Create from guide
└── admin_users.html       ⚠️  Create from guide
```

## Navbar Integration

Add to `base.html` navbar:

```html
{% if current_library and current_user.is_admin_of(current_library.id) %}
<a href="/admin/{{ current_library.slug }}" style="color: #fbbf24;">
    ⚡ Admin Panel
</a>
{% endif %}
```

## Testing Checklist

- [ ] Login as admin
- [ ] See "⚡ Admin Panel" in navbar
- [ ] Click admin link
- [ ] Dashboard loads with stats
- [ ] Can toggle seat maintenance
- [ ] Can update settings
- [ ] Settings save successfully
- [ ] Reports display data
- [ ] Can view all bookings
- [ ] Can cancel any booking
- [ ] Non-admin users blocked

## Database Queries

**Check admin status**:
```sql
SELECT username, is_csr_super_admin FROM user;
```

**Make user CSR Super Admin**:
```sql
UPDATE user SET is_csr_super_admin = 1 WHERE username = 'admin';
```

**Check library admins**:
```sql
SELECT u.username, l.name, la.role 
FROM library_admin la
JOIN user u ON la.user_id = u.id
JOIN library l ON la.library_id = l.id;
```

## Permissions Logic

```python
# Check if user is admin
current_user.is_admin_of(library.id)

# Returns True if:
# - User is CSR Super Admin, OR
# - User has LibraryAdmin record with role='admin'

# Check if user is staff
current_user.is_staff_of(library.id)

# Returns True if:
# - User is CSR Super Admin, OR
# - User has LibraryAdmin record (any role)
```

## Common Issues

**"Access denied"**:
→ Check `is_csr_super_admin` flag or LibraryAdmin record

**No admin link**:
→ Verify `current_user.is_admin_of(library.id)` in template

**Stats show 0**:
→ Create test bookings first

**Blueprint not found**:
→ Check `app.register_blueprint(admin_bp)` in app.py

## Color Codes

- 🟢 Green: Available/Active
- 🔴 Red: Maintenance/Cancelled  
- 🟡 Yellow: Admin/Warning
- ⚫ Gray: Disabled/Inactive

## Success Criteria

✅ Can access `/admin/bpsmv`
✅ Dashboard shows statistics
✅ Can toggle maintenance
✅ Settings save correctly
✅ Reports display data
✅ Non-admins see error

---

**Ready?** Add `admin.py`, update `models.py`, register blueprint! 🚀
