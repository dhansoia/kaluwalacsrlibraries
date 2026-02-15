# 🔐 Authentication & Library Selector Setup Guide

## Overview

This update adds a complete authentication system with:
- ✅ User registration and login
- ✅ Library selector on login/register
- ✅ Multi-library context detection
- ✅ Library-specific dashboards
- ✅ Role-based access (foundation)
- ✅ Responsive, DU-style forms

## 📦 Files to Download

### Core Files (Required)
1. **models_with_auth.py** → Replace `models.py`
2. **app_with_auth.py** → Replace `app.py`
3. **seed_users.py** → New file (test users)

### Templates (Required - Create `templates/` folder)
4. **base.html** → `templates/base.html`
5. **login.html** → `templates/login.html`
6. **register.html** → `templates/register.html`
7. **dashboard.html** → `templates/dashboard.html`
8. **switch_library.html** → `templates/switch_library.html`
9. **library_detail.html** → `templates/library_detail.html`

## 🚀 Installation Steps

### Step 1: Create Templates Folder
```powershell
cd C:\Users\hcl\desktop\kaluwala_csr
mkdir templates
```

### Step 2: Place All Template Files
Copy all `.html` files into the `templates/` folder:
```
kaluwala_csr/
├── templates/                  ← NEW folder
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── switch_library.html
│   └── library_detail.html
├── models.py                   ← REPLACE
├── app.py                      ← REPLACE
├── seed_users.py               ← NEW
└── ... (other files)
```

### Step 3: Replace Core Files
```powershell
# Backup existing files (optional)
copy models.py models.py.backup
copy app.py app.py.backup

# Replace with new versions
# (Download and copy models_with_auth.py as models.py)
# (Download and copy app_with_auth.py as app.py)
```

### Step 4: Update Database Schema
```powershell
# Activate virtual environment
.\venv\Scripts\Activate

# Delete old database to apply new schema
del instance\kaluwala.db

# Run migration to recreate database
python migrate.py
```

### Step 5: Seed Test Users
```powershell
python seed_users.py
```

### Step 6: Start Application
```powershell
python app.py
```

## ✅ What's New

### Updated User Model
```python
# New fields added to User model:
- is_active: Boolean (default True)
- home_library_id: Foreign key to Library
- get_id(): Returns user ID as string for Flask-Login

# New methods:
- get_accessible_libraries(): Returns list of libraries user can access
```

### Authentication Routes

#### `/login` (GET/POST)
- Username + Password + Library Selector
- Validates credentials
- Checks if user is active
- Redirects to library dashboard on success

#### `/register` (GET/POST)
- Username, Email, Password, Confirm Password
- Home Library Selector
- Password validation (min 6 chars)
- Auto-login after registration

#### `/logout`
- Logs out user
- Redirects to login page

#### `/switch-library`
- Shows all available libraries
- Highlights user's home library
- Quick access to any library

### Library Context Detection

The app automatically detects library from URL:
- `/bpsmv/dashboard` → Sets `g.current_library` to BPSMV
- `/libraries/bpsmv` → Sets `g.current_library` to BPSMV
- Available in all templates as `{{ current_library }}`

### Protected Routes

#### `/<slug>/dashboard`
- Requires login
- Requires library context
- Shows library stats and info
- User's personalized dashboard

#### `/<slug>/bookings`
- Requires login
- Requires library context
- Placeholder for booking management

## 🧪 Testing Guide

### Test 1: Register New User
1. Visit: http://localhost:5000/register
2. Fill form:
   - Username: `myusername`
   - Email: `my@email.com`
   - Password: `mypass123`
   - Confirm Password: `mypass123`
   - Home Library: BPSMV
3. Click "Create Account"
4. Should auto-login and redirect to dashboard

**Expected Result:**
- ✅ Account created
- ✅ Auto-logged in
- ✅ Redirected to `/bpsmv/dashboard`
- ✅ Welcome message with username

### Test 2: Login with Admin
1. Visit: http://localhost:5000/login
2. Credentials:
   - Username: `admin`
   - Password: `admin123`
   - Library: BPSMV
3. Click "Sign In"

**Expected Result:**
- ✅ Logged in successfully
- ✅ Redirected to `/bpsmv/dashboard`
- ✅ Navbar shows admin name and logout

### Test 3: Login with Test User
1. Visit: http://localhost:5000/login
2. Credentials:
   - Username: `student1`
   - Password: `password123`
   - Library: BPSMV
3. Click "Sign In"

**Expected Result:**
- ✅ Logged in successfully
- ✅ Dashboard shows stats
- ✅ Can view bookings, seats, etc.

### Test 4: Dashboard Features
After logging in, check:
- [ ] Library name in navbar
- [ ] Library logo displays
- [ ] Welcome message with username
- [ ] Stats cards show correct numbers
- [ ] Library info section populated
- [ ] Operating hours displayed
- [ ] Quick action buttons work

### Test 5: Library Selector
1. Login as any user
2. Click "Switch Library" in navbar
3. Should see all libraries with logos
4. Home library has "HOME" badge
5. Click any library card
6. Should navigate to that library's dashboard

### Test 6: Logout
1. While logged in, click "Logout"
2. Should redirect to login page
3. Trying to access `/bpsmv/dashboard` should redirect to login
4. Login message should appear

### Test 7: Navbar Behavior
- **Logged out**: No navbar
- **Logged in**: 
  - Shows library logo
  - Shows library name and location
  - Shows username
  - Shows Dashboard, Bookings, Switch Library links
  - Shows Logout button

### Test 8: Library Context
Test URL patterns:
- `/bpsmv/dashboard` ✅ Works
- `/libraries/bpsmv` ✅ Works (public view)
- `/invalid/dashboard` ✅ Shows error or redirects
- `/login` ✅ No library context needed

## 📊 Database Changes

### Before Migration:
```sql
User table:
- id, username, email, password_hash, created_at
```

### After Migration:
```sql
User table:
- id, username, email, password_hash, created_at
- is_active (NEW)
- home_library_id (NEW)
```

## 🔑 Test Accounts

After running `seed_users.py`:

| Username | Password | Email | Role | Library |
|----------|----------|-------|------|---------|
| admin | admin123 | admin@bpsmv.ac.in | Admin | BPSMV |
| student1 | password123 | student1@example.com | User | BPSMV |
| student2 | password123 | student2@example.com | User | BPSMV |
| testuser | test123 | test@example.com | User | BPSMV |

## 🎨 UI Features

### Login Page
- Clean, centered design
- Library selector dropdown
- Shows library info on selection
- "Don't have account? Register" link
- Responsive mobile layout

### Register Page
- All fields validated
- Password confirmation
- Email format validation
- Username uniqueness check
- Home library selection
- "Already have account? Login" link

### Dashboard
- Personalized welcome message
- Library marquee message
- 4 stat cards:
  - Total seats
  - Available seats
  - My active bookings
  - Slots per day
- Library information section
- Operating hours section
- Quick action buttons

### Navbar (when logged in)
- Library logo + name
- Dashboard link
- My Bookings link
- Switch Library link
- Username display
- Logout button
- Fully responsive

## 🔒 Security Features

### Implemented:
- ✅ Password hashing (Werkzeug)
- ✅ Session management (Flask-Login)
- ✅ CSRF protection (Flask built-in)
- ✅ Login required decorators
- ✅ User active status check
- ✅ Password length validation
- ✅ Email format validation

### To Add (Future):
- [ ] Password strength requirements
- [ ] Rate limiting for login attempts
- [ ] Email verification
- [ ] Password reset functionality
- [ ] Two-factor authentication
- [ ] Session timeout

## 🐛 Troubleshooting

### Issue: "Template not found"
**Solution**: Make sure `templates/` folder exists and all `.html` files are inside it.

### Issue: "User table has no column 'is_active'"
**Solution**: 
1. Delete `instance/kaluwala.db`
2. Run `python migrate.py`
3. Run `python seed_users.py`

### Issue: "Library not found" on dashboard
**Solution**: URL must match library slug exactly (e.g., `/bpsmv/dashboard` not `/BPSMV/dashboard`)

### Issue: Login form doesn't show libraries
**Solution**: Run `python migrate.py` to create BPSMV library first.

### Issue: Redirect loop on login
**Solution**: Clear browser cookies/cache, or use incognito mode.

### Issue: Navbar not showing
**Solution**: Check `base.html` is in templates folder and has `{% if current_user.is_authenticated %}` block.

## 🎯 Next Development Steps

After authentication is working:

### Phase 1: Booking System
- [ ] Seat selection interface
- [ ] Date and time slot picker
- [ ] Booking creation
- [ ] Booking confirmation

### Phase 2: Booking Management
- [ ] View my bookings
- [ ] Cancel booking
- [ ] Booking history
- [ ] Upcoming bookings

### Phase 3: Admin Features
- [ ] Admin dashboard
- [ ] Manage seats
- [ ] View all bookings
- [ ] User management
- [ ] System settings

### Phase 4: Enhanced Features
- [ ] Email notifications
- [ ] SMS reminders
- [ ] Seat availability calendar
- [ ] Booking statistics
- [ ] Export reports

## 📝 Code Structure

```
kaluwala_csr/
│
├── models.py              # Database models with auth
├── app.py                 # Routes with authentication
├── config.py              # Configuration (unchanged)
├── migrate.py             # Database seeding (unchanged)
├── seed_users.py          # Test user seeding (NEW)
│
├── templates/             # Jinja2 templates (NEW)
│   ├── base.html         # Base template with navbar
│   ├── login.html        # Login form
│   ├── register.html     # Registration form
│   ├── dashboard.html    # User dashboard
│   ├── switch_library.html  # Library selector
│   └── library_detail.html  # Public library view
│
├── static/                # Static assets
│   ├── kaluwala_logo.jpg
│   └── bpsmv_logo.png
│
└── instance/              # Database
    └── kaluwala.db
```

## 🌐 URL Routes Map

### Public Routes (No Login Required)
- `/` → Redirects to login or dashboard
- `/login` → Login form
- `/register` → Registration form
- `/libraries/<slug>` → Public library view
- `/health` → Health check

### Protected Routes (Login Required)
- `/logout` → Logout
- `/switch-library` → Library selector
- `/<slug>/dashboard` → Library dashboard
- `/<slug>/bookings` → User's bookings (placeholder)

## ✅ Verification Checklist

Setup is complete when:
- [ ] Can visit http://localhost:5000/login
- [ ] Login page shows library selector
- [ ] Can register new account
- [ ] Can login with admin credentials
- [ ] Can login with test user credentials
- [ ] Dashboard loads with correct library info
- [ ] Navbar shows library name and logo
- [ ] Stats cards show numbers
- [ ] Can switch between libraries
- [ ] Logout works and redirects to login
- [ ] Trying to access dashboard while logged out redirects to login

## 🎉 Success!

If all tests pass, you now have:
- ✅ Complete authentication system
- ✅ User registration and login
- ✅ Library selector
- ✅ Multi-library support
- ✅ Protected routes
- ✅ Personalized dashboards
- ✅ Professional UI/UX
- ✅ Mobile responsive design

Ready to build the booking system! 🚀
