# 🔬 Enable Researcher & Staff Reserved Seats - Complete Guide

## Overview
This will enable CSR admins to reserve specific seats for researchers and staff with visual color coding.

## ⚠️ IMPORTANT: Database Schema Update Required

Your current database doesn't have the new seat categories. You MUST recreate the database.

## 📦 Step-by-Step Setup

### Step 1: Backup Current Data (Optional)
```powershell
# If you have important bookings, backup first
copy instance\kaluwala.db instance\kaluwala.db.backup
```

### Step 2: Update models.py

**Replace your current models.py with models_admin.py**

The key change is in the SeatCategory enum:
```python
class SeatCategory(enum.Enum):
    general = 'general'
    reserved = 'reserved'
    researcher = 'researcher'  # NEW
    staff = 'staff'           # NEW
```

### Step 3: Delete Old Database
```powershell
del instance\kaluwala.db
```

### Step 4: Recreate Database
```powershell
python migrate.py
```

This will:
- Create fresh database with new schema
- Add BPSMV library with 60 seats
- Create admin user (admin/admin123)
- Set up system settings

### Step 5: Make Admin CSR Super Admin
```powershell
python
```

```python
from models import db, User
from app import create_app

app = create_app()
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    admin.is_csr_super_admin = True
    db.session.commit()
    print("✓ Admin is CSR Super Admin!")

exit()
```

### Step 6: Replace Files

Download and replace:
1. **models_admin.py** → Rename to **models.py**
2. **csr_admin_FULL.py** → Rename to **csr_admin.py** (with full reservation code)
3. **csr_libraries_FULL.html** → Rename to **csr_libraries.html** (with reservation UI)
4. **seats.html** (updated with researcher/staff colors)

### Step 7: Restart App
```powershell
python app.py
```

## ✅ Test the Feature

### Test 1: Access Seat Reservations
1. Login as admin
2. Go to CSR Admin → Manage All Libraries
3. Find BPSMV library card
4. You should see **TWO** sections:
   - Adjust Seat Capacity
   - Reserved Seat Allocation ← NEW

### Test 2: Allocate Reserved Seats
In "Reserved Seat Allocation":
- For Researchers: Enter `10`
- For Staff: Enter `5`
- Click "Update Reservations"

**Expected:**
- ✅ Success: "Seat reservations updated: 10 for researchers, 5 for staff"
- ✅ Shows: "Reserved: 15 / 60 seats"

### Test 3: View in Booking Page
1. Go to: `/bpsmv/seats`
2. Select any date/time
3. Look at seat colors

**Expected:**
- Seats 1-45: 🟢 Green (General)
- Seats 46-55: 🟣 Purple (Researcher)
- Seats 56-60: 🔴 Pink (Staff)
- Legend shows all 6 categories

## 🎨 What You'll See

### Library Management Card
```
┌─────────────────────────────────────┐
│ BPSMV Library                       │
│ 📍 Sonipat, Haryana                │
│                                     │
│ [60] Seats │ [100] Bookings │ [5]  │
│                                     │
│ Adjust Seat Capacity                │
│ [ 60 ] [Update]                     │
│                                     │
│ Reserved Seat Allocation      ← NEW │
│ For Researchers: [ 10 ]             │
│ For Staff:       [  5 ]             │
│ [Update Reservations]               │
│ Reserved: 15 / 60 seats             │
└─────────────────────────────────────┘
```

### Booking Page Legend
```
🟢 Available (General)
🔴 Booked
🟠 Reserved Category
🟣 Researcher Only  ← NEW
🔴 Staff Only       ← NEW
⚫ Maintenance
```

## 🔒 Validation Rules

✅ **Allowed:**
- 0 to total_seats for each category
- Researcher + Staff ≤ Total Seats
- Re-allocate anytime (if no active bookings)

❌ **Blocked:**
- Negative numbers
- Total reservations > Total seats
- Changing seats with future bookings

## 📊 Allocation Logic

Seats are assigned from **highest numbers first**:

**Example: 60 total seats, 10 researchers, 5 staff**
```
Seat 1-45:  General (green)
Seat 46-55: Researcher (purple)
Seat 56-60: Staff (pink)
```

## ⚡ Quick Commands

```powershell
# Complete setup from scratch
del instance\kaluwala.db
python migrate.py
python verify_csr_admin.py
python app.py
```

## 🎯 Files You Need

1. **models_admin.py** - Has researcher/staff enum
2. **csr_admin.py** - Full version with reservation routes
3. **csr_libraries.html** - With reservation UI (uncommented)
4. **seats.html** - With purple/pink colors
5. **verify_csr_admin.py** - Auto-sets CSR super admin

## 🐛 Troubleshooting

### Error: "AttributeError: researcher"
**Cause:** Using new code with old database
**Fix:** Delete database and run migrate.py

### Error: "column not found"
**Cause:** Database schema doesn't match models
**Fix:** Delete database and run migrate.py

### Reservation Controls Not Showing
**Cause:** Using commented version of templates
**Fix:** Download full version (uncommented)

### Can't Update Reservations
**Cause:** Route is commented out
**Fix:** Use full csr_admin.py with route enabled

## ✅ Success Checklist

- [ ] Deleted old database
- [ ] models.py has researcher/staff in SeatCategory
- [ ] Ran migrate.py successfully
- [ ] Set admin as CSR super admin
- [ ] csr_admin.py has update_reservations route
- [ ] csr_libraries.html shows reservation controls
- [ ] seats.html has purple/pink CSS
- [ ] App restarted
- [ ] Can see reservation form
- [ ] Can allocate seats
- [ ] See colored seats in booking page

## 🎉 When It's Working

You'll know it's working when:
- ✅ Manage Libraries page shows reservation controls
- ✅ Can set researcher and staff seat counts
- ✅ Success message after updating
- ✅ Purple and pink seats appear in booking page
- ✅ Legend shows all 6 seat types
- ✅ Seat allocation updates dynamically

Ready to enable this feature! 🚀
