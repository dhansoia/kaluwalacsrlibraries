#!/usr/bin/env python3
"""
Fix BPSMV Library Seats
Convert all reserved/researcher/staff seats to general seats

Usage:
    python fix_bpsmv_seats.py
"""

from app import create_app
from models import db, Library, Seat, SeatCategory, Booking, BookingStatus
from datetime import date

def fix_bpsmv_seats():
    """Convert all special category seats to general for BPSMV library"""
    
    app = create_app('production')
    
    with app.app_context():
        print("\n" + "="*60)
        print("BPSMV Library - Seat Category Fix")
        print("="*60 + "\n")
        
        # Find BPSMV library
        bpsmv = Library.query.filter_by(slug='bpsmv').first()
        
        if not bpsmv:
            print("❌ Error: BPSMV library not found")
            print("Available libraries:")
            for lib in Library.query.all():
                print(f"  - {lib.name} (slug: {lib.slug})")
            return
        
        print(f"✓ Found library: {bpsmv.name} (ID: {bpsmv.id})")
        print()
        
        # Get seat statistics BEFORE
        total_seats = Seat.query.filter_by(library_id=bpsmv.id).count()
        general_seats_before = Seat.query.filter_by(
            library_id=bpsmv.id,
            category=SeatCategory.general
        ).count()
        reserved_seats_before = Seat.query.filter_by(
            library_id=bpsmv.id,
            category=SeatCategory.reserved
        ).count()
        researcher_seats_before = Seat.query.filter_by(
            library_id=bpsmv.id,
            category=SeatCategory.researcher
        ).count()
        staff_seats_before = Seat.query.filter_by(
            library_id=bpsmv.id,
            category=SeatCategory.staff
        ).count()
        
        print("Current Seat Distribution:")
        print(f"  Total Seats:      {total_seats}")
        print(f"  General (Green):  {general_seats_before}")
        print(f"  Reserved (Orange): {reserved_seats_before}")
        print(f"  Researcher (Blue): {researcher_seats_before}")
        print(f"  Staff (Purple):    {staff_seats_before}")
        print()
        
        # Find all non-general seats
        seats_to_convert = Seat.query.filter_by(library_id=bpsmv.id).filter(
            Seat.category != SeatCategory.general
        ).all()
        
        if not seats_to_convert:
            print("✓ All seats are already general. No changes needed.")
            return
        
        print(f"Converting {len(seats_to_convert)} seats to general...")
        print()
        
        # Check for active bookings on these seats
        active_bookings_count = 0
        for seat in seats_to_convert:
            active_bookings = Booking.query.filter_by(
                seat_id=seat.id,
                status=BookingStatus.booked
            ).filter(Booking.date >= date.today()).count()
            
            if active_bookings > 0:
                active_bookings_count += active_bookings
                print(f"  ⚠️  Seat {seat.number} ({seat.category.value}) has {active_bookings} active booking(s)")
        
        if active_bookings_count > 0:
            print(f"\n  ℹ️  Total active bookings on these seats: {active_bookings_count}")
            print(f"     These bookings will remain valid after conversion.\n")
        
        # Convert all seats to general
        converted_count = 0
        for seat in seats_to_convert:
            old_category = seat.category.value
            seat.category = SeatCategory.general
            converted_count += 1
            print(f"  ✓ Seat {seat.number:>3}: {old_category:>10} → general")
        
        # Commit changes
        try:
            db.session.commit()
            print()
            print("="*60)
            print(f"✅ SUCCESS: Converted {converted_count} seats to general")
            print("="*60)
            print()
            
            # Get seat statistics AFTER
            general_seats_after = Seat.query.filter_by(
                library_id=bpsmv.id,
                category=SeatCategory.general
            ).count()
            
            print("New Seat Distribution:")
            print(f"  Total Seats:      {total_seats}")
            print(f"  General (Green):  {general_seats_after}")
            print(f"  Reserved (Orange): 0")
            print(f"  Researcher (Blue): 0")
            print(f"  Staff (Purple):    0")
            print()
            print("All seats in BPSMV library are now GENERAL (green) seats.")
            print("All students can book any seat.")
            
        except Exception as e:
            db.session.rollback()
            print()
            print("="*60)
            print(f"❌ ERROR: Failed to update seats")
            print(f"Error details: {str(e)}")
            print("="*60)
            raise

if __name__ == '__main__':
    fix_bpsmv_seats()
