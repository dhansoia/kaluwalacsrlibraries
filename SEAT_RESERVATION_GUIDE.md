# 🔬 Reserved Seats for Researchers & Staff

## Feature Overview

CSR Super Admins can now designate specific seats for:
- 🔬 **Researchers** - Reserved for research scholars
- 👔 **Staff** - Reserved for library staff/faculty

## 📦 Files to Update

1. **models_admin.py** - Updated SeatCategory enum
2. **csr_admin.py** - Added reservation management route
3. **templates/csr_libraries.html** - Added reservation controls
4. **templates/seats.html** - Added visual indicators

## 🎨 Seat Color Coding

| Color | Category | Who Can Book |
|-------|----------|--------------|
| 🟢 Green | General | Everyone |
| 🟠 Orange | Reserved | Reserved category users |
| 🟣 Purple | Researcher | Researchers only |
| 🔴 Pink | Staff | Staff only |
| ⚫ Gray | Maintenance | No one |
| 🔴 Red | Booked | No one (already taken) |

## 🚀 How to Use

### Step 1: Database Update Required

**IMPORTANT:** The database schema changed. You need to:

```powershell
# Option A: Delete and recreate database (loses data)
del instance\kaluwala.db
python migrate.py

# Option B: Manual SQL update (preserves data)
# Not recommended unless you have important data
```

### Step 2: Access Reservation Management

1. Login as CSR Super Admin
2. Go to: `http://localhost:5000/csr-admin/libraries`
3. Each library card now has 2 sections:
   - **Adjust Seat Capacity** (total seats)
   - **Reserved Seat Allocation** (researchers & staff) ← NEW

### Step 3: Allocate Reserved Seats

**Example: BPSMV Library (60 seats)**

```
Reserved Seat Allocation
┌─────────────────────────────────────┐
│ For Researchers: [ 10 ]             │
│ For Staff:       [  5 ]             │
│ [Update Reservations]               │
│ Reserved: 15 / 60 seats             │
└─────────────────────────────────────┘
```

**Enter numbers:**
- Researchers: `10`
- Staff: `5`
- Click "Update Reservations"

**Result:**
- ✅ 10 seats marked as "researcher" (purple)
- ✅ 5 seats marked as "staff" (pink)
- ✅ 45 seats remain "general" (green)

## 📊 Allocation Logic

### How Seats Are Assigned

The system allocates from the **highest seat numbers** first:

**Example: 60 total seats**
- Set 10 for researchers + 5 for staff
- Seats 56-60 → Staff (5 seats, pink)
- Seats 51-55 → Researcher (10 seats, purple)  
- Seats 1-50 → General (45 seats, green)

### Validation Rules

✅ **Allowed:**
- Any number from 0 to total seats
- Researcher + Staff ≤ Total Seats

❌ **Blocked:**
- Negative numbers
- Researcher + Staff > Total Seats
- Changing seats with active bookings

## 🧪 Testing Guide

### Test 1: Set Reservations

1. Go to `/csr-admin/libraries`
2. Find BPSMV (60 seats)
3. Set:
   - Researchers: `10`
   - Staff: `5`
4. Click "Update Reservations"

**Expected:**
- ✅ Success: "Seat reservations updated: 10 for researchers, 5 for staff"
- ✅ Counter shows: "Reserved: 15 / 60 seats"

### Test 2: View in Booking Page

1. Go to `/bpsmv/seats`
2. Select any date/time
3. Look at seat map

**Expected:**
- ✅ Seats 1-45: Green (general)
- ✅ Seats 46-55: Purple (researcher)
- ✅ Seats 56-60: Pink (staff)
- ✅ Legend shows all categories

### Test 3: Validation - Too Many Reserved

1. Library has 60 seats
2. Set Researchers: `40`
3. Set Staff: `30` (total = 70)
4. Click "Update Reservations"

**Expected:**
- ❌ Error: "Total reservations (70) cannot exceed total seats (60)"
- ❌ No changes made

### Test 4: Change Allocation

1. Current: 10 researchers, 5 staff
2. Change to: 15 researchers, 10 staff
3. Click "Update Reservations"

**Expected:**
- ✅ Previous allocations cleared
- ✅ New allocations applied
- ✅ Seats renumbered accordingly

### Test 5: Remove Reservations

1. Set Researchers: `0`
2. Set Staff: `0`
3. Click "Update Reservations"

**Expected:**
- ✅ All seats become general (green)
- ✅ Reserved: 0 / 60 seats

### Test 6: Protected Seats

1. Book seat #60 (staff seat) for tomorrow
2. Try to reduce staff seats from 5 to 3
3. Click "Update Reservations"

**Expected:**
- ❌ Error: "Not enough available seats... Some seats have active bookings"
- ❌ Allocations not changed

## 🎯 Use Cases

### Research University
```
Total: 200 seats
Researchers: 50 (25%)
Staff: 20 (10%)
General: 130 (65%)
```

### Public Library
```
Total: 100 seats
Researchers: 0 (0%)
Staff: 10 (10%)
General: 90 (90%)
```

### College Library
```
Total: 80 seats
Researchers: 20 (25%)
Staff: 10 (12.5%)
General: 50 (62.5%)
```

## 📱 User Experience

### For Regular Users

When booking, they see:
- **Purple seats**: Label says "Researcher" (maybe restricted)
- **Pink seats**: Label says "Staff" (maybe restricted)
- Can still click and try to book
- System can implement restrictions in future

### For Researchers/Staff

*Future Enhancement:*
- Add "user_type" field to User model
- Restrict purple seats to users with type="researcher"
- Restrict pink seats to users with type="staff"

## 🔒 Current Behavior

**As of now:**
- Seats are visually marked
- Different colors in booking interface
- No booking restrictions yet
- All users can book any available seat

**Future Enhancement:**
- Add user type verification
- Restrict bookings based on seat category
- Show "For Researchers Only" message

## 📝 Database Schema

### SeatCategory Enum
```python
class SeatCategory(enum.Enum):
    general = 'general'      # Everyone
    reserved = 'reserved'    # Original reserved
    researcher = 'researcher' # NEW
    staff = 'staff'          # NEW
```

### Seat Table (Unchanged)
```sql
CREATE TABLE seat (
    id INTEGER PRIMARY KEY,
    library_id INTEGER NOT NULL,
    number VARCHAR(20) NOT NULL,
    category VARCHAR(20) NOT NULL,  -- Can be: general, reserved, researcher, staff
    in_maintenance BOOLEAN DEFAULT 0
);
```

## ✅ Setup Checklist

- [ ] Update models.py with new SeatCategory values
- [ ] Replace csr_admin.py with updated version
- [ ] Replace csr_libraries.html template
- [ ] Replace seats.html template  
- [ ] Delete old database (or migrate schema)
- [ ] Run migrate.py to recreate
- [ ] Restart app
- [ ] Test reservation allocation
- [ ] Verify colors in booking page

## 🎨 Visual Reference

### Library Management Page
```
┌──────────────────────────────────────────┐
│ BPSMV Library                            │
│ 📍 Sonipat, Haryana                     │
│                                          │
│ [60] Total │ [100] Bookings │ [5] Active│
│                                          │
│ Adjust Seat Capacity                     │
│ [ 60 ] [Update]                          │
│                                          │
│ Reserved Seat Allocation          ← NEW  │
│ For Researchers: [ 10 ]                  │
│ For Staff:       [  5 ]                  │
│ [Update Reservations]                    │
│ Reserved: 15 / 60 seats                  │
└──────────────────────────────────────────┘
```

### Booking Page
```
Legend:
🟢 Available  🔴 Booked  🟠 Reserved
🟣 Researcher Only  🔴 Staff Only  ⚫ Maintenance

Seat Grid:
[1🟢] [2🟢] [3🟢] ... [45🟢]    ← General
[46🟣] [47🟣] ... [55🟣]         ← Researcher
[56🔴] [57🔴] ... [60🔴]         ← Staff
```

## 🚀 Next Steps

### Phase 1: Basic Allocation (✅ Current)
- Visual seat categorization
- CSR admin can allocate
- Color coding in UI

### Phase 2: User Types (Future)
- Add user_type field to User model
- Options: general, researcher, staff
- Set during registration or by admin

### Phase 3: Booking Restrictions (Future)
- Check user_type before allowing booking
- Show error: "This seat is reserved for researchers"
- Allow admins to override restrictions

### Phase 4: Advanced Features (Future)
- Temporary reservations (time-based)
- Department-specific seats
- Priority booking for certain types
- Quota management

Perfect for academic institutions! 🎓🔬
