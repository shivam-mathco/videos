import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
import os


class EmailSender:
    def __init__(self, sender_email, app_password):
        self.sender_email = sender_email
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, receiver_email, subject, body):
        """
        Send HTML email only

        Args:
            receiver_email (str): Recipient email address
            subject (str): Email subject
            body (str): Email body (HTML format only)

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Create message container
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = receiver_email

            # Attach only HTML version
            html_part = MIMEText(body, "html", "utf-8")
            msg.attach(html_part)

            # Connect to SMTP server and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.app_password)
            server.send_message(msg)
            server.quit()

            return True, f"Email sent successfully to {receiver_email}"

        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed. Check your email and app password."
        except smtplib.SMTPException as e:
            return False, f"SMTP error occurred: {str(e)}"
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"


# app.py
app = Flask(__name__)

EMAIL_CONFIG = {
    "sender_email": os.getenv("SENDER_EMAIL", "your_email@gmail.com"),
    "app_password": os.getenv("APP_PASSWORD", "your_app_password"),
}


@app.route("/v2/send-email", methods=["POST"])
def send_email():
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify({"status": "error", "message": "No JSON payload received"}),
                400,
            )

        required_fields = ["receiver_email", "subject", "body"]
        for field in required_fields:
            if field not in data:
                return jsonify({"status": "error", "message": f"Missing {field}"}), 400

        email_sender = EmailSender(
            EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["app_password"]
        )

        success, message = email_sender.send_email(
            data["receiver_email"], data["subject"], data["body"]
        )

        status_code = 200 if success else 500
        return (
            jsonify({"status": True if success else False, "message": message}),
            status_code,
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
