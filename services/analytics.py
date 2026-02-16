"""
Analytics Service Module
Provides network-wide metrics, library statistics, and data export capabilities
"""

import csv
import io
from datetime import datetime, date, timedelta
from flask import make_response
from models import db, Library, Seat, Booking, User, BookingStatus, SeatCategory, SystemSettings
from sqlalchemy import func, and_, or_, extract, cast, String

class AnalyticsService:
    """Service class for analytics and reporting"""
    
    @staticmethod
    def get_network_summary():
        """Get overall network statistics"""
        total_libraries = Library.query.count()
        total_seats = Seat.query.count()
        total_users = User.query.count()
        total_bookings = Booking.query.count()
        active_bookings = Booking.query.filter_by(status=BookingStatus.booked).filter(
            Booking.date >= date.today()
        ).count()
        
        return {
            'total_libraries': total_libraries,
            'total_seats': total_seats,
            'total_users': total_users,
            'total_bookings': total_bookings,
            'active_bookings': active_bookings
        }
    
    @staticmethod
    def get_library_utilization(library_id=None, days=30):
        """
        Calculate utilization percentage for libraries
        Utilization = (Total Bookings / (Total Seats * Days * Slots per Day)) * 100
        """
        start_date = date.today() - timedelta(days=days)
        
        if library_id:
            libraries = [Library.query.get(library_id)]
        else:
            libraries = Library.query.all()
        
        utilization_data = []
        
        for library in libraries:
            # Get total seats
            total_seats = Seat.query.filter_by(library_id=library.id).count()
            
            # Get system settings for slots calculation
            settings = SystemSettings.query.filter_by(library_id=library.id).first()
            if not settings:
                continue
            
            # Calculate slots per day
            hours = settings.closing_time.hour - settings.opening_time.hour
            slots_per_day = (hours * 60) // settings.slot_duration
            
            # Get total bookings in period
            total_bookings = Booking.query.filter(
                Booking.library_id == library.id,
                Booking.date >= start_date,
                Booking.date <= date.today()
            ).count()
            
            # Calculate maximum possible bookings
            actual_days = (date.today() - start_date).days + 1
            max_bookings = total_seats * actual_days * slots_per_day
            
            # Calculate utilization percentage
            utilization = (total_bookings / max_bookings * 100) if max_bookings > 0 else 0
            
            utilization_data.append({
                'library_id': library.id,
                'library_name': library.name,
                'library_slug': library.slug,
                'total_seats': total_seats,
                'total_bookings': total_bookings,
                'max_bookings': max_bookings,
                'utilization_percent': round(utilization, 2),
                'days_analyzed': actual_days
            })
        
        return utilization_data
    
    @staticmethod
    def get_daily_bookings(library_id=None, days=30):
        """Get daily booking trends"""
        start_date = date.today() - timedelta(days=days)
        
        query = db.session.query(
            Booking.date,
            func.count(Booking.id).label('count')
        ).filter(
            Booking.date >= start_date,
            Booking.date <= date.today()
        )
        
        if library_id:
            query = query.filter(Booking.library_id == library_id)
        
        results = query.group_by(Booking.date).order_by(Booking.date).all()
        
        return [
            {
                'date': booking_date.strftime('%Y-%m-%d'),
                'count': count
            }
            for booking_date, count in results
        ]
    
    @staticmethod
    def get_monthly_bookings(library_id=None, months=6):
        """Get monthly booking trends - PostgreSQL compatible"""
        start_date = date.today() - timedelta(days=months * 30)
        
        # Use PostgreSQL to_char instead of SQLite strftime
        # Format: to_char(date_column, 'YYYY-MM')
        query = db.session.query(
            func.to_char(Booking.date, 'YYYY-MM').label('month'),
            func.count(Booking.id).label('count')
        ).filter(
            Booking.date >= start_date
        )
        
        if library_id:
            query = query.filter(Booking.library_id == library_id)
        
        results = query.group_by('month').order_by('month').all()
        
        return [
            {
                'month': month,
                'count': count
            }
            for month, count in results
        ]
    
    @staticmethod
    def get_library_rankings(metric='bookings', days=30):
        """Get libraries ranked by a specific metric"""
        start_date = date.today() - timedelta(days=days)
        
        if metric == 'bookings':
            # Rank by total bookings
            results = db.session.query(
                Library.id,
                Library.name,
                Library.slug,
                func.count(Booking.id).label('value')
            ).join(Booking).filter(
                Booking.date >= start_date
            ).group_by(Library.id).order_by(func.count(Booking.id).desc()).all()
        
        elif metric == 'users':
            # Rank by unique users
            results = db.session.query(
                Library.id,
                Library.name,
                Library.slug,
                func.count(func.distinct(Booking.user_id)).label('value')
            ).join(Booking).filter(
                Booking.date >= start_date
            ).group_by(Library.id).order_by(func.count(func.distinct(Booking.user_id)).desc()).all()
        
        elif metric == 'seats':
            # Rank by total seats
            results = db.session.query(
                Library.id,
                Library.name,
                Library.slug,
                func.count(Seat.id).label('value')
            ).join(Seat).group_by(Library.id).order_by(func.count(Seat.id).desc()).all()
        
        else:
            return []
        
        return [
            {
                'library_id': lib_id,
                'library_name': lib_name,
                'library_slug': lib_slug,
                'value': value,
                'rank': idx + 1
            }
            for idx, (lib_id, lib_name, lib_slug, value) in enumerate(results)
        ]
    
    @staticmethod
    def get_booking_status_breakdown(library_id=None):
        """Get breakdown of bookings by status"""
        query = db.session.query(
            Booking.status,
            func.count(Booking.id).label('count')
        )
        
        if library_id:
            query = query.filter(Booking.library_id == library_id)
        
        results = query.group_by(Booking.status).all()
        
        return {
            status.value: count
            for status, count in results
        }
    
    @staticmethod
    def export_bookings_csv(library_id=None, start_date=None, end_date=None):
        """Export bookings data to CSV"""
        query = Booking.query
        
        if library_id:
            query = query.filter_by(library_id=library_id)
        
        if start_date:
            query = query.filter(Booking.date >= start_date)
        
        if end_date:
            query = query.filter(Booking.date <= end_date)
        
        bookings = query.order_by(Booking.date.desc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Booking ID', 'Library', 'User', 'Seat Number', 
            'Date', 'Time Slot', 'Status', 'Created At'
        ])
        
        # Write data
        for booking in bookings:
            writer.writerow([
                booking.id,
                booking.library.name,
                booking.user.username,
                booking.seat.number,
                booking.date.strftime('%Y-%m-%d'),
                booking.time_slot.strftime('%H:%M'),
                booking.status.value,
                booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=bookings_{datetime.now().strftime("%Y%m%d")}.csv'
        
        return response
    
    @staticmethod
    def export_libraries_csv():
        """Export libraries data to CSV"""
        libraries = Library.query.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Library ID', 'Name', 'Slug', 'City', 'State', 
            'Total Seats', 'Contact Email', 'Contact Phone', 'Created At'
        ])
        
        # Write data
        for library in libraries:
            total_seats = Seat.query.filter_by(library_id=library.id).count()
            writer.writerow([
                library.id,
                library.name,
                library.slug,
                library.city,
                library.state,
                total_seats,
                library.contact_email or '',
                library.contact_phone or '',
                library.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=libraries_{datetime.now().strftime("%Y%m%d")}.csv'
        
        return response
    
    @staticmethod
    def get_peak_hours(library_id=None, days=30):
        """Get peak booking hours - PostgreSQL compatible"""
        start_date = date.today() - timedelta(days=days)
        
        # Use PostgreSQL to_char instead of SQLite strftime
        # Format: to_char(time_column, 'HH24') for 24-hour format
        query = db.session.query(
            func.to_char(Booking.time_slot, 'HH24').label('hour'),
            func.count(Booking.id).label('count')
        ).filter(
            Booking.date >= start_date
        )
        
        if library_id:
            query = query.filter(Booking.library_id == library_id)
        
        results = query.group_by('hour').order_by('hour').all()
        
        return [
            {
                'hour': f"{hour}:00",
                'count': count
            }
            for hour, count in results
        ]
    
    @staticmethod
    def get_user_statistics():
        """Get user-related statistics"""
        total_users = User.query.count()
        active_users = db.session.query(func.count(func.distinct(Booking.user_id))).filter(
            Booking.date >= date.today() - timedelta(days=30)
        ).scalar()
        
        csr_admins = User.query.filter_by(is_csr_super_admin=True).count()
        
        # Top users by booking count
        top_users = db.session.query(
            User.username,
            func.count(Booking.id).label('booking_count')
        ).join(Booking, User.id == Booking.user_id).group_by(User.id).order_by(
            func.count(Booking.id).desc()
        ).limit(10).all()
        
        return {
            'total_users': total_users,
            'active_users_30d': active_users,
            'csr_admins': csr_admins,
            'top_users': [
                {'username': username, 'bookings': count}
                for username, count in top_users
            ]
        }
