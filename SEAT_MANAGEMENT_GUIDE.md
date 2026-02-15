# 💺 Seat Capacity Management Guide

## Feature: Dynamic Seat Allocation

CSR Super Admins can now adjust seat capacity for any library from 10 to 500 seats.

## 📦 Files to Update

1. **csr_admin.py** - Updated with `/update-seats` route
2. **templates/csr_libraries.html** - NEW template with seat controls

## 🚀 How to Use

### Access Seat Management

1. Login as CSR Super Admin
2. Go to CSR Admin Dashboard
3. Click "🏢 Manage All Libraries"
4. You'll see all libraries with seat controls

### Update Seat Capacity

**For Each Library Card:**
- Shows current seat count
- Input field to change capacity
- "Update" button
- Range: 10-500 seats

**Example: Increase Seats**
```
BPSMV Library
Current: 60 seats
Change to: 100 seats
Click "Update"
→ Adds 40 new seats (numbered 61-100)
→ Auto-assigns 75% general, 25% reserved
```

**Example: Decrease Seats**
```
Pilot Library  
Current: 80 seats
Change to: 50 seats
Click "Update"
→ Removes seats 51-80 (if no active bookings)
→ Warns if seats have active bookings
```

## ✅ Features

### Smart Seat Addition
- Automatically numbers new seats
- Maintains 75% general / 25% reserved ratio
- New seats marked as available (not in maintenance)

### Safe Seat Removal
- ✅ Only removes seats from the end (highest numbers)
- ✅ Checks for active bookings first
- ✅ Prevents deletion if seats have future bookings
- ✅ Shows error message if removal blocked

### Validation
- Minimum: 10 seats
- Maximum: 500 seats
- Integer values only
- Must be different from current count

## 🧪 Testing

### Test 1: Add Seats
1. Go to Manage Libraries
2. Find BPSMV (60 seats)
3. Change to 80
4. Click Update

**Expected:**
- ✅ "Added 20 seats to BPSMV. Total: 80"
- ✅ Seats 61-80 created
- ✅ Seat 61-75 = general
- ✅ Seat 76-80 = reserved

### Test 2: Remove Unused Seats
1. Find library with 100 seats
2. Change to 80
3. Click Update

**Expected:**
- ✅ "Removed 20 seats from [Library]. Total: 80"
- ✅ Seats 81-100 deleted
- ✅ Database cleaned

### Test 3: Try to Remove Booked Seats
1. Book seat #100 for tomorrow
2. Try to reduce from 100 to 90 seats
3. Click Update

**Expected:**
- ❌ Error: "Cannot remove seats with active bookings"
- ❌ Seat #100 has 1 active booking
- ❌ No seats removed

### Test 4: Invalid Range
1. Try to set seats to 5 (too low)
2. Click Update

**Expected:**
- ❌ Error: "Seat capacity must be between 10 and 500"

## 📊 Use Cases

### Small Library (Community Center)
- Start: 10 seats
- Grow as needed: 20, 30, 50 seats
- Based on demand

### Medium Library (College)
- Start: 60 seats
- Peak semester: Increase to 100
- Summer: Reduce to 40

### Large Library (University)
- Start: 200 seats
- Can expand to 500
- Different wings/floors

## 🎯 Business Logic

### Adding Seats
```python
Current: 60 seats
New Total: 100 seats
→ Create seats 61-100 (40 new seats)
→ General: 61-75 (75% of 100 = 75 total)
→ Reserved: 76-100 (25% of 100 = 25 total)
```

### Removing Seats
```python
Current: 100 seats
New Total: 80 seats
→ Check seats 81-100 for active bookings
→ If clean: Delete seats 81-100
→ If booked: Block removal + show error
```

## 🔒 Safety Features

1. **Booking Protection**: Can't remove seats with future bookings
2. **Range Validation**: 10-500 only
3. **Order Preservation**: Always remove from end
4. **Category Balance**: Auto-maintains 75/25 ratio
5. **Error Messages**: Clear feedback on failures

## 💡 Tips

**Before Reducing Seats:**
- Check for active bookings
- Cancel future bookings if needed (from admin panel)
- Then reduce capacity

**When Expanding:**
- New seats immediately available
- Appear in booking interface
- Auto-numbered sequentially

**Monitoring:**
- View total bookings per library
- See active bookings count
- Check utilization before adjusting

## 📝 Database Changes

### When Adding Seats
```sql
INSERT INTO seat (library_id, number, category, in_maintenance)
VALUES (1, '61', 'general', 0),
       (1, '62', 'general', 0),
       ...
       (1, '76', 'reserved', 0);
```

### When Removing Seats
```sql
DELETE FROM seat 
WHERE library_id = 1 
  AND number IN ('81', '82', ..., '100')
  AND id NOT IN (
    SELECT DISTINCT seat_id 
    FROM booking 
    WHERE status = 'booked' 
      AND date >= CURRENT_DATE
  );
```

## ✅ Success Criteria

Seat management working when:
- [ ] Can access Manage Libraries page
- [ ] See current seat count for each library
- [ ] Can increase seat capacity
- [ ] New seats appear in booking system
- [ ] Can decrease capacity (if no bookings)
- [ ] Error shown when removing booked seats
- [ ] Validation works (10-500 range)
- [ ] Success messages appear

## 🎉 Benefits

1. **Flexibility**: Adjust capacity based on demand
2. **Safety**: Protection against data loss
3. **Automation**: Auto-numbering and categorization
4. **Scalability**: Support 10-500 seats per library
5. **Real-time**: Changes apply immediately

Perfect for libraries with changing capacity needs! 💺✨
