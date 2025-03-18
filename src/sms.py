import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
import json

def send_notifications(self, listings):
    # Load the JSON config
    with open('data/onfig.json', 'r') as f:
        config = json.load(f)
    notifications = config.get('notifications', {})
    
    # Check required notification fields
    email = notifications.get('email')
    phone = notifications.get('phone')
    if not email or not phone:
        print("Error: Email or phone number missing in config.json.")
        return
    
    # Prepare the message content
    message_body = "New listings found:\n" + "\n".join([f"{l['title']} - {l['price']}" for l in listings])
    
    # Send Email
    msg = MIMEText(message_body)
    msg['Subject'] = "New Car Listings Found"
    msg['From'] = "your_email@example.com"
    msg['To'] = email
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login("your_email@example.com", "your_password")
        server.send_message(msg)
    
    # Send SMS via Twilio
    account_sid = "your_twilio_sid"
    auth_token = "your_twilio_token"
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"Found {len(listings)} new listings!",
        from_="your_twilio_number",
        to=phone
    )
    print("Notifications sent!")