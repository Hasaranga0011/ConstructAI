import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.sender_email = os.getenv("EMAIL_SENDER", "your-email@gmail.com")
        self.sender_password = os.getenv("EMAIL_PASSWORD", "your-app-password")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_password_reset_email(self, recipient_email: str, reset_token: str):
        """Send password reset email"""
        try:
            reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
            
            subject = "ConstructAI - Password Reset Request"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #1e40af;">ConstructAI Password Reset</h2>
                        <p>Hi there,</p>
                        <p>We received a request to reset your password. Click the link below to reset it:</p>
                        <p>
                            <a href="{reset_link}" 
                               style="display: inline-block; padding: 10px 20px; background-color: #1e40af; color: white; text-decoration: none; border-radius: 5px;">
                                Reset Password
                            </a>
                        </p>
                        <p style="color: #666; font-size: 12px;">
                            This link will expire in 1 hour.<br>
                            If you didn't request this, please ignore this email.
                        </p>
                        <p>Best regards,<br>ConstructAI Team</p>
                    </div>
                </body>
            </html>
            """
            
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            message.attach(MIMEText(html_content, "html"))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False

email_service = EmailService()