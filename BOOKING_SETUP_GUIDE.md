# 🎫 Per-Library Booking Engine Setup Guide

## Overview

This update adds a complete seat booking system with:
- ✅ Visual seat map with real-time availability
- ✅ Date and time slot picker
- ✅ Interactive seat selection
- ✅ Booking validation (conflicts, maintenance, limits)
- ✅ Booking management (view, cancel)
- ✅ Library-scoped bookings (g.current_library)
- ✅ Beautiful responsive UI

## 📦 Files to Download

### Core Files
1. **app_booking.py** → Replace `app.py`

### New Templates
2. **seats.html** → `templates/seats.html` (NEW)
3. **my_bookings.html** → `templates/my_bookings.html` (NEW)

### Keep Existing
- All other templates (base.html, login.html, etc.)
- models.py (no changes needed)
- migrate.py, config.py, etc.

## 🚀 Installation Steps

### Step 1: Backup Current Files
```powershell
# Backup existing app.py
copy app.py app.py.backup
```

### Step 2: Replace app.py
```powershell
# Download app_booking.py and rename to app.py
# Place in project root
```

### Step 3: Add New Templates
```powershell
# Place in templates/ folder
# - seats.html
# - my_bookings.html
```

Your folder structure should be:
```
kaluwala_csr/
├── templates/
│   ├── base.html              (existing)
│   ├── login.html             (existing)
│   ├── register.html          (existing)
│   ├── dashboard.html         (existing)
│   ├── switch_library.html    (existing)
│   ├── library_detail.html    (existing)
│   ├── seats.html             ⭐ NEW
│   └── my_bookings.html       ⭐ NEW
├── app.py                     ⭐ UPDATED
└── ... (other files)
```

### Step 4: Restart Application
```powershell
# Make sure venv is activated
.\venv\Scripts\Activate

# Start app
python app.py
```

## ✨ New Features

### 1. Seat Selection Page (`/<slug>/seats`)

**Route**: `/bpsmv/seats?date=2026-02-13&time_slot=09:00:00`

**Features**:
- Date picker (today onwards)
- Time slot dropdown (based on library settings)
- Visual seat grid with color coding:
  - 🟢 Green = Available
  - 🔴 Red = Booked
  - 🟠 Orange = Reserved category (available)
  - ⚫ Gray = Under maintenance
- Click to select seat
- Real-time availability check
- Responsive grid layout

**Validations**:
- Can't book past dates
- Can't book maintenance seats
- Can't book already booked seats
- One booking per user per time slot

### 2. Book Seat Endpoint (`POST /<slug>/book`)

**Validations**:
- ✅ Seat exists and belongs to library
- ✅ Seat is not in maintenance
- ✅ Slot is not already booked
- ✅ User doesn't have another booking for same slot
- ✅ Date is not in the past
- ✅ Valid date and time format

**On Success**:
- Creates booking record
- Redirects to "My Bookings"
- Shows success message

### 3. My Bookings Page (`/<slug>/bookings`)

**Sections**:
- **Upcoming Bookings**: Active future bookings
- **Booking History**: Past and cancelled bookings

**Information Displayed**:
- Seat number and category
- Date and time
- Library name
- Booking ID
- Status (Active/Cancelled/Completed)
- Booking creation date

**Actions**:
- Cancel active bookings
- View booking details

### 4. Cancel Booking (`POST /bookings/<id>/cancel`)

**Validations**:
- ✅ Booking belongs to current user
- ✅ Booking is active (not already cancelled)
- ✅ Booking is not in the past

**On Success**:
- Updates status to "cancelled"
- Frees up the seat
- Shows success message

## 🧪 Testing Guide

### Test 1: View Seat Map
1. Login as any user (student1/password123)
2. Click "Dashboard" for BPSMV
3. Click "📅 Book a Seat" button
4. Should see seat selection page

**Expected**:
- ✅ Date picker shows today's date
- ✅ Time slots dropdown populated
- ✅ Seat grid displays (60 seats)
- ✅ Legend shows color meanings
- ✅ Seats are clickable

### Test 2: Select Different Date/Time
1. On seats page, change date to tomorrow
2. Select different time slot
3. Click "Show Available Seats"

**Expected**:
- ✅ Page reloads with new date/time
- ✅ Seat availability updates
- ✅ URL reflects selected date/time

### Test 3: Book a Seat
1. On seats page, click any green (available) seat
2. Booking form appears below
3. Verify details are correct
4. Click "🎫 Confirm Booking"

**Expected**:
- ✅ Success message appears
- ✅ Redirects to My Bookings
- ✅ New booking shows in "Upcoming Bookings"

### Test 4: View Same Slot Again
1. Go back to seats page
2. Select same date/time as your booking

**Expected**:
- ✅ Your booked seat now shows as RED
- ✅ Clicking it does nothing (not selectable)
- ✅ Other seats still green/available

### Test 5: Try Double Booking
1. Try to book another seat for SAME time slot
2. Click "Confirm Booking"

**Expected**:
- ✅ Error message: "You already have a booking for this time slot"
- ✅ Booking is NOT created
- ✅ Stays on seats page

### Test 6: Cancel Booking
1. Go to "My Bookings" from navbar
2. Find an upcoming booking
3. Click "❌ Cancel Booking"
4. Confirm cancellation

**Expected**:
- ✅ Success message appears
- ✅ Booking moves to "Booking History"
- ✅ Status shows "Cancelled"
- ✅ Seat becomes available again

### Test 7: Book Cancelled Seat
1. After cancelling, go to seats page
2. Select same date/time
3. Find the seat you cancelled

**Expected**:
- ✅ Seat is GREEN (available) again
- ✅ Can be booked by you or others

### Test 8: Past Date Validation
1. Try to manually change URL date to yesterday
2. Try to book a seat

**Expected**:
- ✅ Error: "Cannot book seats for past dates"
- ✅ Booking is NOT created

### Test 9: Maintenance Seat
1. Manually set a seat to maintenance in database:
   ```sql
   UPDATE seat SET in_maintenance = 1 WHERE id = 1;
   ```
2. View seats page

**Expected**:
- ✅ Seat shows as GRAY
- ✅ Not clickable
- ✅ Legend shows "Maintenance"

### Test 10: Reserved Category
1. Seats 46-60 are reserved category
2. View seats page

**Expected**:
- ✅ Show as ORANGE if available
- ✅ Still bookable
- ✅ Show "Reserved" label

### Test 11: Multiple Users
1. Login as student1, book seat 10
2. Logout, login as student2
3. Try to book seat 10 for same slot

**Expected**:
- ✅ Seat 10 shows as RED (booked)
- ✅ Not clickable
- ✅ Can book different seat

### Test 12: Empty Bookings
1. Login with new account (no bookings)
2. Go to "My Bookings"

**Expected**:
- ✅ Shows empty state
- ✅ "No Upcoming Bookings" message
- ✅ "Book a Seat Now" button
- ✅ History section also empty

## 📊 Database Queries

### Check All Bookings
```sql
SELECT 
    b.id,
    u.username,
    s.number as seat_number,
    b.date,
    b.time_slot,
    b.status
FROM booking b
JOIN user u ON b.user_id = u.id
JOIN seat s ON b.seat_id = s.id
ORDER BY b.date DESC, b.time_slot DESC;
```

### Check Seat Availability
```sql
SELECT 
    s.number,
    s.category,
    s.in_maintenance,
    COUNT(b.id) as bookings_count
FROM seat s
LEFT JOIN booking b ON s.id = b.seat_id 
    AND b.date = '2026-02-13'
    AND b.time_slot = '09:00:00'
    AND b.status = 'booked'
WHERE s.library_id = 1
GROUP BY s.id
ORDER BY s.number;
```

### User's Active Bookings
```sql
SELECT 
    s.number,
    b.date,
    b.time_slot,
    b.status
FROM booking b
JOIN seat s ON b.seat_id = s.id
WHERE b.user_id = 2
    AND b.status = 'booked'
    AND b.date >= date('now')
ORDER BY b.date, b.time_slot;
```

## 🎨 UI Features

### Seat Map Design
- **Grid Layout**: Auto-responsive based on screen size
- **Color Coding**: Instant visual status
- **Hover Effects**: 3D lift on available seats
- **Selection**: Blue border with glow
- **Click Feedback**: Smooth animations

### Booking Form
- **Slide-in Animation**: Appears when seat selected
- **Info Box**: Blue background with booking details
- **Large Button**: Clear call-to-action
- **Cancel Option**: Easy to change selection

### My Bookings
- **Card Layout**: Each booking in separate card
- **Status Badges**: Color-coded pills
- **Action Buttons**: Primary action (cancel)
- **Empty States**: Friendly messages when no bookings

## 🔒 Security & Validation

### Implemented Checks
1. **Authentication**: All routes require login
2. **Library Context**: Bookings scoped to g.current_library
3. **Ownership**: Users can only cancel their bookings
4. **Date Validation**: No past dates
5. **Time Validation**: Valid time slot format
6. **Conflict Detection**: No double bookings
7. **Maintenance Check**: Can't book maintenance seats
8. **Status Check**: Can't cancel non-active bookings

### Validation Flow
```
User clicks "Book"
    ↓
Check user logged in ✓
    ↓
Check library context ✓
    ↓
Check seat exists ✓
    ↓
Check seat available ✓
    ↓
Check not in maintenance ✓
    ↓
Check no conflicts ✓
    ↓
Check user limit ✓
    ↓
Create booking ✓
```

## 🐛 Troubleshooting

### Issue: Seats page shows no seats
**Solution**: Run migration to create seats
```powershell
python migrate.py
```

### Issue: Time slots empty
**Solution**: Check SystemSettings exists for library
```sql
SELECT * FROM system_settings WHERE library_id = 1;
```

### Issue: Can't click any seats
**Solution**: Make sure seats are not all in maintenance
```sql
UPDATE seat SET in_maintenance = 0;
```

### Issue: "Template not found: seats.html"
**Solution**: Make sure seats.html is in templates/ folder

### Issue: Booking form doesn't appear
**Solution**: Check browser console for JavaScript errors

### Issue: Date picker doesn't work
**Solution**: Make sure using modern browser (Chrome, Firefox, Edge)

## 📝 Code Structure

### New Routes
```python
GET  /<slug>/seats           # Seat selection page
POST /<slug>/book            # Create booking
GET  /<slug>/bookings        # My bookings
POST /bookings/<id>/cancel   # Cancel booking
```

### Helper Functions
```python
generate_time_slots()        # Creates time slot list
library_context_required()   # Ensures g.current_library set
```

### Validation Logic
```python
# In book_seat():
- Check past dates
- Check seat exists
- Check maintenance
- Check conflicts
- Check user limit
```

## 🎯 Next Steps

After booking system is working:

### Phase 1: Admin Features
- [ ] View all bookings
- [ ] Cancel any booking
- [ ] Mark seats as maintenance
- [ ] View booking statistics

### Phase 2: Enhanced Booking
- [ ] Multi-slot booking (all day)
- [ ] Recurring bookings (weekly)
- [ ] Waiting list
- [ ] Priority booking for reserved

### Phase 3: Notifications
- [ ] Email confirmation
- [ ] SMS reminders
- [ ] Cancellation notifications
- [ ] Booking expiry warnings

### Phase 4: Analytics
- [ ] Usage heatmaps
- [ ] Popular time slots
- [ ] User booking patterns
- [ ] Occupancy reports

## ✅ Success Criteria

Your booking system is working when:
- [ ] Can view seat map with colors
- [ ] Can select date and time
- [ ] Can click and select available seat
- [ ] Booking form appears on selection
- [ ] Can confirm and create booking
- [ ] Booked seat turns red
- [ ] Booking appears in "My Bookings"
- [ ] Can cancel active bookings
- [ ] Cancelled seat becomes available
- [ ] Can't book same slot twice
- [ ] Can't book maintenance seats
- [ ] Can't book past dates

## 🎉 Features Summary

### User Experience
- 🎨 Beautiful visual seat map
- 🖱️ One-click seat selection
- 📅 Easy date/time picker
- 💚 Real-time availability
- 📱 Mobile responsive
- ⚡ Fast and smooth

### Business Logic
- 🔒 Conflict prevention
- ✅ Validation at every step
- 🏢 Multi-library support
- 👥 Multi-user safe
- 📊 Full audit trail
- 🔄 Status tracking

### Technical
- 🎯 Clean code structure
- 🛡️ Security focused
- 📦 Modular design
- 🔌 Easy to extend
- 🧪 Testable
- 📝 Well documented

Ready to book some seats! 🚀📚
