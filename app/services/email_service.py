import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    
    @staticmethod
    def send_reset_password_email(recipient_email: str, reset_token: str):
        """Send password reset email with reset link"""
        try:
            # Get email credentials from environment
            sender_email = os.getenv("EMAIL_SENDER", "your-email@gmail.com")
            sender_password = os.getenv("EMAIL_PASSWORD", "your-app-password")
            
            # Check if credentials are configured
            if sender_email == "your-email@gmail.com" or sender_password == "your-app-password":
                print("\n" + "="*80)
                print("📧 PASSWORD RESET EMAIL (DEMO MODE - Email Not Configured)")
                print("="*80)
                print(f"To: {recipient_email}")
                print(f"Subject: ConstructAI - Password Reset Request")
                print(f"\nReset Token: {reset_token}")
                print(f"Reset Link: http://localhost:5173/forgot-password?token={reset_token}&email={recipient_email}")
                print("="*80 + "\n")
                print("⚠️ To send real emails, set EMAIL_SENDER and EMAIL_PASSWORD in .env file")
                print("See EMAIL_SETUP_GUIDE.md for instructions\n")
                return True
            
            reset_link = f"http://localhost:5173/forgot-password?token={reset_token}&email={recipient_email}"
            
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
                        <p style="color: #666; font-size: 14px;">
                            Or copy this link:<br>
                            <code>{reset_link}</code>
                        </p>
                        <p style="color: #666; font-size: 12px;">
                            This link will expire in 1 hour.<br>
                            If you didn't request this, please ignore this email.
                        </p>
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                        <p>Best regards,<br><strong>ConstructAI Team</strong></p>
                    </div>
                </body>
            </html>
            """
            
            text_content = f"""
            ConstructAI Password Reset
            
            Hi there,
            
            We received a request to reset your password. Click the link below to reset it:
            {reset_link}
            
            This link will expire in 10 minutes.
            If you didn't request this, please ignore this email.
            
            Best regards,
            ConstructAI Team
            """
            
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = sender_email
            message["To"] = recipient_email
            
            message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            # Send email via SMTP
            print(f"📧 Sending password reset email to {recipient_email}...")
            
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, message.as_string())
            
            print(f"✅ Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            # Print to console as fallback
            print("\n" + "="*80)
            print("📧 PASSWORD RESET EMAIL (EMAIL SENDING FAILED - Using Console)")
            print("="*80)
            print(f"To: {recipient_email}")
            print(f"Subject: ConstructAI - Password Reset Request")
            print(f"\nReset Token: {reset_token}")
            print(f"Reset Link: http://localhost:5173/forgot-password?token={reset_token}&email={recipient_email}")
            print("="*80 + "\n")
            return True