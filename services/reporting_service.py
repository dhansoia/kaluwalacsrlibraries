"""
Reporting Service
Handles user check-in and auto-cancellation for no-shows
"""

from datetime import datetime, timedelta
from models import db, Booking, BookingStatus, NoShowHistory

class ReportingService:
    
    @staticmethod
    def mark_as_reported(booking_id, admin_user_id):
        """Admin marks that user has reported to library"""
        booking = Booking.query.get(booking_id)
        
        if not booking:
            return False, "Booking not found"
        
        if booking.status != BookingStatus.booked:
            return False, "Booking is not active"
        
        if booking.is_reported:
            return False, "User already reported"
        
        # Check if still within grace period
        if booking.is_grace_period_expired():
            return False, "Grace period expired. Booking should be auto-cancelled."
        
        # Mark as reported
        booking.is_reported = True
        booking.reported_at = datetime.now()
        booking.reported_by_admin = admin_user_id
        
        db.session.commit()
        
        return True, "User marked as reported successfully"
    
    @staticmethod
    def auto_cancel_expired_bookings(library_id=None):
        """Auto-cancel bookings where user didn't report within grace period"""
        from datetime import date
        
        # Query for today's bookings that should be cancelled
        query = Booking.query.filter(
            Booking.status == BookingStatus.booked,
            Booking.is_reported == False,
            Booking.date == date.today()
        )
        
        if library_id:
            query = query.filter_by(library_id=library_id)
        
        bookings = query.all()
        
        cancelled_count = 0
        
        for booking in bookings:
            if booking.should_auto_cancel():
                # Auto-cancel the booking
                booking.status = BookingStatus.cancelled
                booking.no_show = True
                booking.auto_cancelled_at = datetime.now()
                booking.cancellation_reason = "No-show: User did not report within 15 minutes"
                
                # Record no-show in history
                no_show = NoShowHistory(
                    user_id=booking.user_id,
                    library_id=booking.library_id,
                    booking_id=booking.id,
                    booking_date=booking.date,
                    booking_time=booking.time_slot,
                    seat_number=booking.seat.number
                )
                
                db.session.add(no_show)
                cancelled_count += 1
        
        db.session.commit()
        
        return cancelled_count
    
    @staticmethod
    def get_pending_reports(library_id):
        """Get all bookings waiting for user to report"""
        from datetime import date
        
        bookings = Booking.query.filter(
            Booking.library_id == library_id,
            Booking.date == date.today(),
            Booking.status == BookingStatus.booked,
            Booking.is_reported == False
        ).order_by(Booking.time_slot.asc()).all()
        
        # Add time remaining for each
        results = []
        for booking in bookings:
            booking_datetime = datetime.combine(booking.date, booking.time_slot)
            grace_end = booking_datetime + timedelta(minutes=booking.grace_period_minutes)
            
            time_remaining = grace_end - datetime.now()
            minutes_remaining = int(time_remaining.total_seconds() / 60)
            
            results.append({
                'booking': booking,
                'minutes_remaining': minutes_remaining,
                'grace_expired': minutes_remaining < 0,
                'can_report': minutes_remaining >= 0
            })
        
        return results
    
    @staticmethod
    def get_reported_today(library_id):
        """Get all bookings that have been reported today"""
        from datetime import date
        
        return Booking.query.filter(
            Booking.library_id == library_id,
            Booking.date == date.today(),
            Booking.is_reported == True
        ).order_by(Booking.reported_at.desc()).all()
    
    @staticmethod
    def get_user_no_show_count(user_id, library_id=None, days=30):
        """Get user's no-show count"""
        from datetime import date, timedelta
        
        start_date = date.today() - timedelta(days=days)
        
        query = NoShowHistory.query.filter(
            NoShowHistory.user_id == user_id,
            NoShowHistory.booking_date >= start_date
        )
        
        if library_id:
            query = query.filter_by(library_id=library_id)
        
        return query.count()
    
    @staticmethod
    def get_upcoming_bookings_needing_report(library_id):
        """Get bookings starting in next 30 minutes that need reporting"""
        from datetime import date
        
        now = datetime.now()
        thirty_min_later = now + timedelta(minutes=30)
        
        bookings = Booking.query.filter(
            Booking.library_id == library_id,
            Booking.date == date.today(),
            Booking.status == BookingStatus.booked,
            Booking.is_reported == False
        ).all()
        
        upcoming = []
        for booking in bookings:
            booking_time = datetime.combine(booking.date, booking.time_slot)
            
            if now <= booking_time <= thirty_min_later:
                upcoming.append(booking)
        
        return upcoming
