import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logger_config import get_logger

logger = get_logger("email_service")

# SMTP Configuration defaults (can be overridden via environment variables)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "jagatic3384@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "").replace(" ", "")
SMTP_FROM = os.environ.get("SMTP_FROM", SMTP_USERNAME)


def send_email(to_email: str, subject: str, body_text: str, body_html: str = None) -> tuple[bool, str]:
    """
    Send an email via SMTP. Falls back to logging if SMTP settings are invalid or connection fails.
    """
    to_email = to_email.strip()
    if not to_email:
        logger.warning("No recipient email provided. Skipping email dispatch.")
        return False, "Recipient email is empty."

    # If credentials are not set, fallback gracefully to log mode
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.info(f"[DEV / OFFLINE EMAIL MODE] To: {to_email} | Subject: {subject}\n{body_text}")
        return True, "Email logged (offline mode)."

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Personal Finance Application <{SMTP_FROM}>"
        msg["To"] = to_email

        msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, [to_email], msg.as_string())

        logger.info(f"Email successfully sent to '{to_email}' with subject '{subject}'.")
        return True, "Email sent successfully."

    except Exception as err:
        logger.error(f"Failed to send email to '{to_email}': {err}", exc_info=True)
        # Also log content so developer/user can see OTP or message in app.log
        logger.info(f"[LOGGED DUE TO SMTP ERROR] To: {to_email} | Subject: {subject}\n{body_text}")
        return False, f"Email delivery failed: {err}"


def send_registration_email(to_email: str, username: str) -> tuple[bool, str]:
    """Send welcome email upon new user account creation."""
    subject = "Welcome to Personal Finance Management System!"

    body_text = (
        f"Hello {username},\n\n"
        f"Thank you for registering with Personal Finance Management System!\n"
        f"Your account '{username}' has been successfully created.\n\n"
        f"You can now log in to track your income, expenses, and manage your budget.\n\n"
        f"Best regards,\nPersonal Finance Team"
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #ffffff;">
          <h2 style="color: #2b5876; margin-top: 0;">Welcome to Personal Finance!</h2>
          <p>Hello <strong>{username}</strong>,</p>
          <p>Thank you for registering with the Personal Finance Management System. Your account has been successfully created!</p>
          <div style="background-color: #f4f7f6; padding: 15px; border-left: 4px solid #2b5876; margin: 20px 0;">
            <p style="margin: 0;"><strong>Username:</strong> {username}</p>
            <p style="margin: 5px 0 0 0;"><strong>Email:</strong> {to_email}</p>
          </div>
          <p>You can now log in to start tracking your income, expenses, and managing your monthly budget.</p>
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
          <p style="font-size: 12px; color: #888;">If you did not create this account, please ignore this email.</p>
        </div>
      </body>
    </html>
    """

    return send_email(to_email, subject, body_text, body_html)


def send_otp_email(to_email: str, username: str, otp: str) -> tuple[bool, str]:
    """Send password reset 6-digit OTP email."""
    subject = f"Your Password Reset OTP: {otp}"

    body_text = (
        f"Hello {username},\n\n"
        f"We received a request to reset the password for your account '{username}'.\n\n"
        f"Your One-Time Password (OTP) is: {otp}\n\n"
        f"This OTP is valid for 5 minutes. Please do not share this code with anyone.\n\n"
        f"Best regards,\nPersonal Finance Team"
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #ffffff;">
          <h2 style="color: #2b5876; margin-top: 0;">Password Reset Request</h2>
          <p>Hello <strong>{username}</strong>,</p>
          <p>We received a request to reset your password. Use the following 6-digit One-Time Password (OTP) to proceed:</p>
          <div style="text-align: center; margin: 25px 0;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #2b5876; background-color: #eef2f5; padding: 10px 20px; border-radius: 6px;">{otp}</span>
          </div>
          <p style="color: #e74c3c;"><strong>Note:</strong> This OTP is valid for <strong>5 minutes</strong>. Do not share this OTP with anyone.</p>
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
          <p style="font-size: 12px; color: #888;">If you did not request a password reset, please secure your account immediately.</p>
        </div>
      </body>
    </html>
    """

    return send_email(to_email, subject, body_text, body_html)


def send_password_changed_email(to_email: str, username: str) -> tuple[bool, str]:
    """Send password changed security alert email."""
    subject = "Security Alert: Your Password Has Been Changed"

    body_text = (
        f"Hello {username},\n\n"
        f"This is to confirm that the password for your account '{username}' has been successfully changed.\n\n"
        f"If you performed this action, no further steps are required.\n"
        f"If you did NOT change your password, please contact support immediately.\n\n"
        f"Best regards,\nPersonal Finance Security Team"
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #ffffff;">
          <h2 style="color: #27ae60; margin-top: 0;">Password Successfully Changed</h2>
          <p>Hello <strong>{username}</strong>,</p>
          <p>Your password for the account <strong>{username}</strong> has been updated successfully.</p>
          <div style="background-color: #eafaf1; padding: 15px; border-left: 4px solid #27ae60; margin: 20px 0;">
            <p style="margin: 0; color: #1e8449;">Your account security details were updated.</p>
          </div>
          <p>If you made this change, you can safely ignore this email. If you did <strong>NOT</strong> initiate this change, please reset your password immediately.</p>
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
          <p style="font-size: 12px; color: #888;">Personal Finance Management System Security Alert</p>
        </div>
      </body>
    </html>
    """

    return send_email(to_email, subject, body_text, body_html)
