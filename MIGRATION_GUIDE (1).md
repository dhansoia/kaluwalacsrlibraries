# 🚀 Database Migration + BPSMV Onboarding Guide

## What's New

### ✨ Features Added
1. **migrate.py** - Database seeding script
2. **Auto-migration** - Runs automatically on first startup
3. **BPSMV Library** - Pre-configured central library
4. **60 Seats** - Auto-generated (45 general, 15 reserved)
5. **System Settings** - 9 AM - 9 PM, 60-minute slots
6. **Admin User** - Default credentials created
7. **Library Detail Page** - `/libraries/<slug>` route

## 📦 Installation Steps

### Step 1: Download New Files
Download these 2 files:
1. **migrate.py** - Migration script
2. **app_with_migration.py** - Updated app with auto-migration

### Step 2: Replace Files
```
kaluwala_csr/
├── migrate.py              ← NEW: Place here
├── app.py                  ← REPLACE with app_with_migration.py (rename it)
└── ... (keep other files)
```

### Step 3: Run Migration (Choose One Method)

#### Method A: Manual Migration (Recommended)
```powershell
# Activate virtual environment
.\venv\Scripts\Activate

# Run migration script
python migrate.py

# Start the app
python app.py
```

#### Method B: Auto-Migration
```powershell
# Just start the app - migration runs automatically if no libraries exist
python app.py
```

## ✅ What Gets Created

### 📚 BPSMV Central Library
- **Name**: BPSMV Central Library
- **Slug**: `bpsmv`
- **Location**: Khanpur Kalan, Sonipat, Haryana - 131305
- **Contact**: library@bpsmv.ac.in, +91-130-2228910
- **CSR Partner**: Kaluwala Constructions Pvt Ltd

### 💺 60 Seats
- **Seats 1-45**: General category (75%)
- **Seats 46-60**: Reserved category (25%)
- **Status**: All active (none in maintenance)

### ⚙️ System Settings
- **Opening Time**: 9:00 AM
- **Closing Time**: 9:00 PM
- **Operating Hours**: 12 hours daily
- **Slot Duration**: 60 minutes
- **Total Slots**: 12 per day
- **Marquee**: "Welcome to BPSMV Central Library - Powered by Kaluwala Constructions"

### 👤 Admin User
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: admin@kaluwala.com
- **Role**: Admin for BPSMV library

## 🧪 Testing

### Test 1: Run Migration
```powershell
python migrate.py
```

**Expected Output:**
```
============================================================
🚀 Kaluwala CSR Libraries - Database Migration
============================================================

📊 Creating database tables...
✓ Database tables ready

📚 Creating BPSMV Central Library...
✓ Created library: BPSMV Central Library (ID: 1)

💺 Creating seats for BPSMV Central Library...
✓ Created 60 seats
  - General seats: 45 (Seats 1-45)
  - Reserved seats: 15 (Seats 46-60)

⚙️  Creating system settings for BPSMV Central Library...
✓ Created system settings
  - Opening time: 9:00 AM
  - Closing time: 9:00 PM
  - Slot duration: 60 minutes
  - Total slots per day: 12

👤 Creating admin user for BPSMV Central Library...
✓ Created admin user
  - Username: admin
  - Email: admin@kaluwala.com
  - Password: admin123
  - User ID: 1
✓ Assigned admin role for BPSMV Central Library

============================================================
✅ Migration Complete!
============================================================

📋 Summary:
  Libraries: 1
  Seats: 60
  Users: 1
  System Settings: 1
  Library Admins: 1

🔑 Admin Credentials:
  Username: admin
  Password: admin123

🌐 Test URLs:
  Main: http://localhost:5000
  BPSMV: http://localhost:5000/libraries/bpsmv
  Health: http://localhost:5000/health
```

### Test 2: Start Application
```powershell
python app.py
```

**Expected Output:**
```
✓ Database tables created successfully

============================================================
🚀 Kaluwala CSR Libraries Network
   Kaluwala Construction Pvt India Ltd
============================================================
📍 Server running at: http://localhost:5000
💾 Database: instance/kaluwala.db
⚙️  Environment: Development
============================================================
```

### Test 3: Visit Home Page
Open browser: **http://localhost:5000**

**Should See:**
- Kaluwala logo (if you added it to static folder)
- "System Ready" status
- Libraries count: 1
- BPSMV Central Library card with "View Details" link

### Test 4: Visit BPSMV Library Page
Open browser: **http://localhost:5000/libraries/bpsmv**

**Should See:**
- Library name and location
- CSR Partner information
- Seating capacity stats (60 total, 45 general, 15 reserved)
- Operating hours (9 AM - 9 PM)
- Booking information (12 slots per day)
- Welcome marquee message

## 🔍 Verification Checklist

After running migration, verify:

- [ ] Home page shows "Libraries: 1"
- [ ] BPSMV library card appears on home page
- [ ] Clicking "View Details" opens library page
- [ ] Library page shows correct address (Khanpur Kalan)
- [ ] Seat stats show: 60 total, 45 general, 15 reserved
- [ ] Operating hours show 9:00 AM - 9:00 PM
- [ ] Marquee message displays correctly
- [ ] Logo appears (if added to static folder)

## 📊 Database Structure After Migration

```
Users Table:
+----+----------+----------------------+---------------+
| ID | Username | Email                | Role          |
+----+----------+----------------------+---------------+
| 1  | admin    | admin@kaluwala.com   | Admin@BPSMV   |
+----+----------+----------------------+---------------+

Libraries Table:
+----+------------------------+-------+------------------+
| ID | Name                   | Slug  | City             |
+----+------------------------+-------+------------------+
| 1  | BPSMV Central Library  | bpsmv | Sonipat          |
+----+------------------------+-------+------------------+

Seats Table:
+----+------------+--------+----------+
| ID | Library ID | Number | Category |
+----+------------+--------+----------+
| 1  | 1          | 1      | general  |
| 2  | 1          | 2      | general  |
...
| 45 | 1          | 45     | general  |
| 46 | 1          | 46     | reserved |
...
| 60 | 1          | 60     | reserved |
+----+------------+--------+----------+

System Settings:
+----+------------+------+------+----------+
| ID | Library ID | Open | Close| Duration |
+----+------------+------+------+----------+
| 1  | 1          | 9:00 | 21:00| 60 min   |
+----+------------+------+------+----------+
```

## 🛠️ Troubleshooting

### Issue: "Library already exists"
**Solution**: Migration is idempotent. Run it again - it will skip existing data.

### Issue: "ImportError: cannot import name 'create_bpsmv_library'"
**Solution**: Make sure `migrate.py` is in the same directory as `app.py`

### Issue: Auto-migration not running
**Solution**: Delete `instance/kaluwala.db` and restart app, or run `python migrate.py` manually

### Issue: 404 on /libraries/bpsmv
**Solution**: 
1. Verify migration completed successfully
2. Check that library with slug 'bpsmv' exists
3. Restart the app

## 🎯 Next Steps

After successful migration:

1. **Test Admin Login** (when auth is built):
   - Username: `admin`
   - Password: `admin123`

2. **Add More Libraries**:
   - Create additional libraries via admin panel
   - Each library gets its own slug URL

3. **Build Authentication**:
   - Login page using Flask-Login
   - Register new users
   - Role-based access control

4. **Implement Booking System**:
   - Seat selection interface
   - Time slot booking
   - Booking management

5. **Create Admin Dashboard**:
   - Manage seats
   - View bookings
   - Configure settings

## 📝 Migration Script Features

The `migrate.py` script is:
- ✅ **Idempotent**: Safe to run multiple times
- ✅ **Smart**: Skips existing data
- ✅ **Informative**: Shows detailed progress
- ✅ **Safe**: Uses transactions
- ✅ **Flexible**: Can be extended for more libraries

## 🔐 Security Note

⚠️ **Important**: The default admin credentials (`admin`/`admin123`) are for development only. In production:

1. Change the admin password immediately
2. Use strong, unique passwords
3. Enable HTTPS
4. Add rate limiting for login attempts
5. Implement password complexity requirements

## 🎉 Success!

If all tests pass, you now have:
- ✅ Fully seeded database
- ✅ BPSMV library configured
- ✅ 60 seats ready for booking
- ✅ Admin user created
- ✅ System settings configured
- ✅ Library detail page working

You're ready to build the authentication and booking features! 🚀
