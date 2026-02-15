"""
Bulk Operations Service
Handles bulk seat management and booking operations
"""

from models import db, Seat, SeatCategory, Booking, BookingStatus
from datetime import date

class BulkOperationsService:
    
    @staticmethod
    def bulk_create_seats(library_id, start_number, end_number, category=SeatCategory.general):
        """Create multiple seats at once"""
        created = []
        errors = []
        
        for num in range(start_number, end_number + 1):
            # Check if seat exists
            existing = Seat.query.filter_by(
                library_id=library_id,
                number=str(num)
            ).first()
            
            if existing:
                errors.append(f"Seat {num} already exists")
                continue
            
            seat = Seat(
                library_id=library_id,
                number=str(num),
                category=category,
                in_maintenance=False
            )
            db.session.add(seat)
            created.append(num)
        
        db.session.commit()
        return created, errors
    
    @staticmethod
    def bulk_update_seat_category(library_id, seat_numbers, new_category):
        """Update category for multiple seats"""
        updated = []
        errors = []
        
        for num in seat_numbers:
            seat = Seat.query.filter_by(
                library_id=library_id,
                number=str(num)
            ).first()
            
            if not seat:
                errors.append(f"Seat {num} not found")
                continue
            
            seat.category = new_category
            updated.append(num)
        
        db.session.commit()
        return updated, errors
    
    @staticmethod
    def bulk_toggle_maintenance(library_id, seat_numbers, maintenance_status):
        """Toggle maintenance for multiple seats"""
        updated = []
        errors = []
        
        for num in seat_numbers:
            seat = Seat.query.filter_by(
                library_id=library_id,
                number=str(num)
            ).first()
            
            if not seat:
                errors.append(f"Seat {num} not found")
                continue
            
            seat.in_maintenance = maintenance_status
            updated.append(num)
        
        db.session.commit()
        return updated, errors
    
    @staticmethod
    def bulk_cancel_bookings(library_id, booking_date):
        """Cancel all bookings for a specific date"""
        bookings = Booking.query.filter_by(
            library_id=library_id,
            date=booking_date,
            status=BookingStatus.booked
        ).all()
        
        cancelled_count = 0
        for booking in bookings:
            booking.status = BookingStatus.cancelled
            cancelled_count += 1
            
            # Send cancellation email (optional - may cause delays if many bookings)
            try:
                from services.email_service import EmailService
                EmailService.send_cancellation_email(booking)
            except:
                pass  # Don't fail if email fails
        
        db.session.commit()
        return cancelled_count
    
    @staticmethod
    def bulk_delete_seats(library_id, seat_numbers):
        """Delete multiple seats (only if no future bookings)"""
        deleted = []
        errors = []
        
        for num in seat_numbers:
            seat = Seat.query.filter_by(
                library_id=library_id,
                number=str(num)
            ).first()
            
            if not seat:
                errors.append(f"Seat {num} not found")
                continue
            
            # Check for future bookings
            future_bookings = Booking.query.filter_by(
                seat_id=seat.id,
                status=BookingStatus.booked
            ).filter(Booking.date >= date.today()).count()
            
            if future_bookings > 0:
                errors.append(f"Seat {num} has {future_bookings} future bookings")
                continue
            
            db.session.delete(seat)
            deleted.append(num)
        
        db.session.commit()
        return deleted, errors
    
    @staticmethod
    def get_bulk_stats(library_id):
        """Get statistics for bulk operations dashboard"""
        total_seats = Seat.query.filter_by(library_id=library_id).count()
        
        general_seats = Seat.query.filter_by(
            library_id=library_id,
            category=SeatCategory.general
        ).count()
        
        researcher_seats = Seat.query.filter_by(
            library_id=library_id,
            category=SeatCategory.researcher
        ).count()
        
        staff_seats = Seat.query.filter_by(
            library_id=library_id,
            category=SeatCategory.staff
        ).count()
        
        maintenance_seats = Seat.query.filter_by(
            library_id=library_id,
            in_maintenance=True
        ).count()
        
        return {
            'total_seats': total_seats,
            'general_seats': general_seats,
            'researcher_seats': researcher_seats,
            'staff_seats': staff_seats,
            'maintenance_seats': maintenance_seats
        }
