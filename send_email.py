import smtplib  # Import the SMTP library to send emails
import os  # Import os to access environment variables


def send_email():
    # Retrieve email credentials from environment variables for security
    email = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")

    # Check if the email and password are set in environment variables
    if not email or not password:
        print("Please set your email and password in environment variables.")
        return

    # Prompt the user to input receiver's email, subject, and message for the email
    receiver_email = input("Enter receiver's email: ")
    subject = input("SUBJECT: ")
    message = input("MESSAGE: ")

    # Prepare the email content (Subject and Message body)
    text = f"Subject: {subject}\n\n{message}"

    try:
        # Connect to Gmail's SMTP server on port 587
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Enable secure TLS (Transport Layer Security) for the connection

        # Log in to the SMTP server using the sender's email and password
        server.login(email, password)

        # Send the email from the sender to the receiver
        server.sendmail(email, receiver_email, text)

        # Notify the user that the email was successfully sent
        print(f"Email has been sent to {receiver_email}")

    except Exception as e:
        # Handle any exceptions (e.g., incorrect credentials, network issues)
        print(f"An error occurred: {e}")

    finally:
        # Always quit the server connection to release resources
        server.quit()


if __name__ == '__main__':
    # Run the send_email function when the script is executed directly
    send_email()
