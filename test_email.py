import os
from flask import Flask
from flask_mail import Mail, Message
from config import config  # Import the config dictionary

# Initialize app with Development settings
app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

mail = Mail(app)

def test_mail():
    with app.app_context():
        # DEBUG: Check if .env values are actually loaded
        print(f"DEBUG: USERNAME = {app.config.get('MAIL_USERNAME')}")
        print(f"DEBUG: TLS      = {app.config.get('MAIL_USE_TLS')}")

        msg = Message(
            subject="Kaluwala CSR Test Email",
            sender=app.config.get('MAIL_DEFAULT_SENDER'),
            recipients=["kaluwalacsrlibraries@gmail.com"],
            body="If you see this, your email configuration is finally working!"
        )

        try:
            print("Attempting to send...")
            mail.send(msg)
            print("✓ Email sent successfully!")
        except Exception as e:
            print(f"✗ Failed: {e}")

if __name__ == "__main__":
    test_mail()