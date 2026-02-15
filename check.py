from app import create_app, mail
from flask_mail import Message

app = create_app()

with app.app_context():
    msg = Message(
        'Test Email',
        recipients=['your-email@gmail.com'],
        html='<h1>Email works!</h1>'
    )
    mail.send(msg)
    print("Email sent successfully!")