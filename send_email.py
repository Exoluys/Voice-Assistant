import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_email(recipient_email, subject, body):
    try:
        # Fetch credentials from environment variables
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('PASSWORD')

        # Validate credentials
        if not sender_email or not sender_password:
            raise ValueError("Email credentials (SENDER_EMAIL and PASSWORD) are missing!")

        # Validate recipient email
        if not recipient_email:
            raise ValueError("Recipient email address is missing!")

        # Set up the server and secure connection
        smtp_server = 'smtp.gmail.com'
        smtp_port = 465  # Using SMTP_SSL for enhanced security

        # Create the email
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body))  # Adding the email body as plain text

        # Send email via secure connection
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())

        print(f"Email sent successfully to {recipient_email}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    recipient = "jairevankar98@gmail.com"
    subject = "Test Email"
    body = "This is a test email."

    # Call the function to send the email
    send_email(recipient, subject, body)
