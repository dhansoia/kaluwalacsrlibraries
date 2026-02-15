"""
PDF Report Generation Service
Creates professional PDF reports for bookings and analytics
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from datetime import datetime, date

class PDFReportService:
    
    @staticmethod
    def generate_booking_report(library, start_date, end_date):
        """Generate PDF report for bookings"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2d5016'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Title
        title = Paragraph(f"<b>Booking Report</b><br/>{library.name}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 10))
        
        # Report Info
        info_style = styles['Normal']
        info_text = f"""
        <b>Report Period:</b> {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}<br/>
        <b>Generated On:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        <b>Library Location:</b> {library.city}, {library.state}<br/>
        <b>Address:</b> {library.address}
        """
        info = Paragraph(info_text, info_style)
        elements.append(info)
        elements.append(Spacer(1, 20))
        
        # Summary Statistics
        from models import Booking, BookingStatus
        
        total_bookings = Booking.query.filter(
            Booking.library_id == library.id,
            Booking.date >= start_date,
            Booking.date <= end_date
        ).count()
        
        completed = Booking.query.filter(
            Booking.library_id == library.id,
            Booking.date >= start_date,
            Booking.date <= end_date,
            Booking.status == BookingStatus.completed
        ).count()
        
        booked = Booking.query.filter(
            Booking.library_id == library.id,
            Booking.date >= start_date,
            Booking.date <= end_date,
            Booking.status == BookingStatus.booked
        ).count()
        
        cancelled = Booking.query.filter(
            Booking.library_id == library.id,
            Booking.date >= start_date,
            Booking.date <= end_date,
            Booking.status == BookingStatus.cancelled
        ).count()
        
        cancellation_rate = (cancelled / total_bookings * 100) if total_bookings > 0 else 0
        
        # Summary Table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Bookings', str(total_bookings)],
            ['Active Bookings', str(booked)],
            ['Completed', str(completed)],
            ['Cancelled', str(cancelled)],
            ['Cancellation Rate', f"{cancellation_rate:.1f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7c2c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(Paragraph("<b>Summary Statistics</b>", styles['Heading2']))
        elements.append(Spacer(1, 10))
        elements.append(summary_table)
        elements.append(Spacer(1, 25))
        
        # Detailed Bookings
        bookings = Booking.query.filter(
            Booking.library_id == library.id,
            Booking.date >= start_date,
            Booking.date <= end_date
        ).order_by(Booking.date.desc()).limit(100).all()
        
        elements.append(Paragraph("<b>Recent Bookings (Last 100)</b>", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        booking_data = [['Date', 'User', 'Seat', 'Time', 'Status']]
        
        for booking in bookings:
            booking_data.append([
                booking.date.strftime('%m/%d/%Y'),
                booking.user.username[:15],  # Truncate long usernames
                f"#{booking.seat.number}",
                booking.time_slot.strftime('%I:%M %p'),
                booking.status.value.title()
            ])
        
        booking_table = Table(booking_data, colWidths=[1.2*inch, 1.8*inch, 0.8*inch, 1.2*inch, 1*inch])
        booking_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7c2c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(booking_table)
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_text = f"""
        <para align=center>
        <font size=8 color="#666666">
        Generated by Kaluwala CSR Libraries Management System<br/>
        Report ID: {library.slug}-{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}<br/>
        Page 1 of 1
        </font>
        </para>
        """
        elements.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_user_activity_report(library, user):
        """Generate PDF report for specific user activity"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(
            f"<b>User Activity Report</b><br/>{user.username}",
            styles['Title']
        )
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # User Stats
        from models import Booking, BookingStatus
        
        total = Booking.query.filter_by(
            user_id=user.id,
            library_id=library.id
        ).count()
        
        active = Booking.query.filter_by(
            user_id=user.id,
            library_id=library.id,
            status=BookingStatus.booked
        ).filter(Booking.date >= date.today()).count()
        
        completed = Booking.query.filter_by(
            user_id=user.id,
            library_id=library.id,
            status=BookingStatus.completed
        ).count()
        
        stats_data = [
            ['Metric', 'Value'],
            ['Total Bookings', str(total)],
            ['Active Bookings', str(active)],
            ['Completed', str(completed)],
            ['Member Since', user.created_at.strftime('%B %d, %Y')],
            ['Email', user.email],
            ['User Role', user.user_role.value.title() if hasattr(user, 'user_role') else 'Student']
        ]
        
        stats_table = Table(stats_data, colWidths=[2.5*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7c2c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        
        elements.append(stats_table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
