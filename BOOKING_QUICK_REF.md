# 🎫 Booking System - Quick Reference

## Installation (3 Steps)
```powershell
# 1. Replace app.py with app_booking.py
# 2. Add seats.html to templates/
# 3. Add my_bookings.html to templates/
python app.py
```

## New Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/bpsmv/seats` | GET | View seat map |
| `/bpsmv/book` | POST | Create booking |
| `/bpsmv/bookings` | GET | My bookings |
| `/bookings/<id>/cancel` | POST | Cancel booking |

## User Flow

```
Login → Dashboard → "Book a Seat"
    ↓
Select Date & Time
    ↓
View Seat Map (60 seats)
    ↓
Click Green Seat
    ↓
Confirm Booking
    ↓
See in "My Bookings"
    ↓
Cancel if needed
```

## Seat Colors

| Color | Status | Can Book? |
|-------|--------|-----------|
| 🟢 Green | Available | ✅ Yes |
| 🔴 Red | Booked | ❌ No |
| 🟠 Orange | Reserved (Available) | ✅ Yes |
| ⚫ Gray | Maintenance | ❌ No |

## Validation Rules

✅ **Allowed**:
- Book any available seat
- Book future dates only
- One booking per slot
- Cancel your active bookings

❌ **Blocked**:
- Past dates
- Already booked seats
- Maintenance seats
- Double booking same slot
- Cancel others' bookings

## Testing Checklist

- [ ] Can view seat map
- [ ] Colors show correctly
- [ ] Can select date/time
- [ ] Can click green seats
- [ ] Form appears on click
- [ ] Can confirm booking
- [ ] See in My Bookings
- [ ] Can cancel booking
- [ ] Seat turns red when booked
- [ ] Seat turns green after cancel

## Test Accounts

```
admin / admin123
student1 / password123
student2 / password123
```

## Key Files

```
app.py                    ← REPLACE
templates/
  ├── seats.html         ← NEW
  └── my_bookings.html   ← NEW
```

## Database Tables Used

- `booking` - Stores reservations
- `seat` - Seat inventory
- `system_settings` - Time slots
- `user` - Who booked
- `library` - Where booked

## Success Indicators

✅ Seat map loads with 60 seats
✅ Can book a seat successfully
✅ Booked seat shows as red
✅ Booking appears in My Bookings
✅ Can cancel and seat becomes available

## Quick Troubleshooting

**No seats showing?**
→ Run `python migrate.py`

**No time slots?**
→ Check SystemSettings exists

**Can't book anything?**
→ Check seats not all in maintenance

**Template error?**
→ Verify files in templates/

## API Examples

### Book a Seat
```html
POST /bpsmv/book
seat_id=10&date=2026-02-13&time_slot=09:00:00
```

### Cancel Booking
```html
POST /bookings/5/cancel
```

## Common Queries

### Check seat availability
```sql
SELECT number, category, in_maintenance
FROM seat 
WHERE library_id = 1
ORDER BY number;
```

### View all bookings
```sql
SELECT s.number, u.username, b.date, b.time_slot
FROM booking b
JOIN seat s ON b.seat_id = s.id
JOIN user u ON b.user_id = u.id
WHERE b.status = 'booked'
ORDER BY b.date, b.time_slot;
```

## Next Features to Build

1. ⭐ Admin dashboard
2. 📊 Booking statistics
3. 📧 Email notifications
4. 📱 SMS reminders
5. 🔄 Recurring bookings

---

**Ready?** Replace app.py, add templates, restart server! 🚀
