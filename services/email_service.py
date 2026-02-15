"""
Email Service for sending notifications
Handles booking confirmations, cancellations, approvals, and reminders
"""

from flask_mail import Message
from flask import current_app, render_template_string
from datetime import datetime

class EmailService:
    
    @staticmethod
    def send_email(to, subject, template):
        """Send email using template"""
        try:
            from app import mail
            
            msg = Message(
                subject=f"[{current_app.config.get('SITE_NAME', 'Kaluwala Libraries')}] {subject}",
                recipients=[to] if isinstance(to, str) else to,
                html=template,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@kaluwala.com')
            )
            
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Email error: {str(e)}")
            return False
    
    @staticmethod
    def send_booking_confirmation(booking):
        """Send booking confirmation email"""
        site_url = current_app.config.get('SITE_URL', 'http://localhost:5000')
        
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .detail {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #10b981; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 0.9em; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Booking Confirmed!</h1>
                </div>
                <div class="content">
                    <p>Dear {booking.user.username},</p>
                    <p>Your seat booking has been confirmed. Here are the details:</p>
                    
                    <div class="detail">
                        <strong>📚 Library:</strong> {booking.library.name}<br>
                        <strong>💺 Seat Number:</strong> {booking.seat.number}<br>
                        <strong>📅 Date:</strong> {booking.date.strftime('%A, %B %d, %Y')}<br>
                        <strong>⏰ Time Slot:</strong> {booking.time_slot.strftime('%I:%M %p')}<br>
                        <strong>📍 Location:</strong> {booking.library.address}, {booking.library.city}
                    </div>
                    
                    <p><strong>Important Reminders:</strong></p>
                    <ul>
                        <li>Please arrive on time for your slot</li>
                        <li>Carry a valid ID for verification</li>
                        <li>Follow library rules and maintain silence</li>
                        <li>Cancel if you cannot make it</li>
                    </ul>
                    
                    <center>
                        <a href="{site_url}/{booking.library.slug}/bookings" class="button">
                            View My Bookings
                        </a>
                    </center>
                    
                    <div class="footer">
                        <p>This is an automated message from Kaluwala CSR Libraries</p>
                        <p>If you didn't make this booking, please contact us immediately.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            to=booking.user.email,
            subject="Seat Booking Confirmation",
            template=template
        )
    
    @staticmethod
    def send_cancellation_email(booking):
        """Send booking cancellation email"""
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .detail {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #ef4444; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❌ Booking Cancelled</h1>
                </div>
                <div class="content">
                    <p>Dear {booking.user.username},</p>
                    <p>Your booking has been cancelled:</p>
                    
                    <div class="detail">
                        <strong>📚 Library:</strong> {booking.library.name}<br>
                        <strong>💺 Seat:</strong> {booking.seat.number}<br>
                        <strong>📅 Date:</strong> {booking.date.strftime('%B %d, %Y')}<br>
                        <strong>⏰ Time:</strong> {booking.time_slot.strftime('%I:%M %p')}
                    </div>
                    
                    <p>You can make a new booking anytime from our website.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            to=booking.user.email,
            subject="Booking Cancelled",
            template=template
        )
    
    @staticmethod
    def send_approval_email(user, library):
        """Send account approval email"""
        site_url = current_app.config.get('SITE_URL', 'http://localhost:5000')
        
        template = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1>✅ Account Approved!</h1>
                </div>
                <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px;">
                    <p>Dear {user.username},</p>
                    <p>Great news! Your account has been approved by {library.name} administration.</p>
                    <p>You can now login and start booking library seats.</p>
                    <center>
                        <a href="{site_url}/login" style="display: inline-block; padding: 12px 24px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px;">
                            Login Now
                        </a>
                    </center>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            to=user.email,
            subject="Account Approved - Start Booking!",
            template=template
        )
    
    @staticmethod
    def send_reminder_email(booking):
        """Send booking reminder (1 day before)"""
        template = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>🔔 Booking Reminder</h2>
                <p>Dear {booking.user.username},</p>
                <p>This is a reminder about your upcoming booking:</p>
                <div style="background: #fef3c7; padding: 15px; border-left: 4px solid #f59e0b; margin: 15px 0;">
                    <strong>Tomorrow:</strong> {booking.date.strftime('%B %d, %Y')}<br>
                    <strong>Time:</strong> {booking.time_slot.strftime('%I:%M %p')}<br>
                    <strong>Seat:</strong> {booking.seat.number}<br>
                    <strong>Library:</strong> {booking.library.name}
                </div>
                <p>Please arrive on time!</p>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            to=booking.user.email,
            subject="Reminder: Your booking is tomorrow",
            template=template
        )
