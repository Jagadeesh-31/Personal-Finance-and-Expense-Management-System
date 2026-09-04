import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logger_config import get_logger

# Step 1: Initialize namespaced logger for email dispatch tracking
logger = get_logger("email_service")

# Step 2: Read SMTP Configuration defaults from environment variables
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "").replace(" ", "")
SMTP_FROM = os.environ.get("SMTP_FROM", SMTP_USERNAME)


# Step 3: Define core email dispatch function via SMTP with offline fallback logging.
def send_email(to_email: str, subject: str, body_text: str, body_html: str = None) -> tuple[bool, str]:
    """
    Send an email via SMTP. Falls back to logging if SMTP settings are invalid or connection fails.
    """
    # Step 3.1: Clean recipient email address
    to_email = to_email.strip()
    if not to_email:
        logger.warning("No recipient email provided. Skipping email dispatch.")
        return False, "Recipient email is empty."

    # Step 3.2: Fallback to log mode if SMTP credentials are missing
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.info(f"[DEV / OFFLINE EMAIL MODE] To: {to_email} | Subject: {subject}\n{body_text}")
        return True, "Email logged (offline mode)."

    try:
        # Step 3.3: Construct MIME Multipart Email Container
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Personal Finance Application <{SMTP_FROM}>"
        msg["To"] = to_email

        # Step 3.4: Attach plain text and optional HTML body parts
        msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))

        # Step 3.5: Establish TLS encrypted SMTP connection and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, [to_email], msg.as_string())

        logger.info(f"Email successfully sent to '{to_email}' with subject '{subject}'.")
        return True, "Email sent successfully."

    except Exception as err:
        # Step 3.6: Handle connection errors gracefully and output body content to log
        logger.error(f"Failed to send email to '{to_email}': {err}", exc_info=True)
        logger.info(f"[LOGGED DUE TO SMTP ERROR] To: {to_email} | Subject: {subject}\n{body_text}")
        return False, f"Email delivery failed: {err}"


# Step 4: Dispatch Welcome Registration Email upon account creation.
def send_registration_email(to_email: str, username: str) -> tuple[bool, str]:
    """Send welcome email upon new user account creation."""
    # Step 4.1: Construct registration subject line
    subject = "Welcome to Personal Finance Management System!"

    # Step 4.2: Construct plain text welcome body
    body_text = (
        f"Hello {username},\n\n"
        f"Thank you for registering with Personal Finance Management System!\n"
        f"Your account '{username}' has been successfully created.\n\n"
        f"You can now log in to track your income, expenses, and manage your budget.\n\n"
        f"Best regards,\nPersonal Finance Team"
    )

    # Step 4.3: Construct HTML template welcome body
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

    # Step 4.4: Trigger email dispatch
    return send_email(to_email, subject, body_text, body_html)


# Step 5: Dispatch 6-digit OTP email for password reset verification.
def send_otp_email(to_email: str, username: str, otp: str) -> tuple[bool, str]:
    """Send password reset 6-digit OTP email."""
    # Step 5.1: Construct OTP subject line
    subject = f"Your Password Reset OTP: {otp}"

    # Step 5.2: Construct plain text OTP body
    body_text = (
        f"Hello {username},\n\n"
        f"We received a request to reset the password for your account '{username}'.\n\n"
        f"Your One-Time Password (OTP) is: {otp}\n\n"
        f"This OTP is valid for 5 minutes. Please do not share this code with anyone.\n\n"
        f"Best regards,\nPersonal Finance Team"
    )

    # Step 5.3: Construct HTML template OTP body
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

    # Step 5.4: Trigger email dispatch
    return send_email(to_email, subject, body_text, body_html)


# Step 6: Dispatch Security Alert Email upon password update.
def send_password_changed_email(to_email: str, username: str) -> tuple[bool, str]:
    """Send password changed security alert email."""
    # Step 6.1: Construct security alert subject line
    subject = "Security Alert: Your Password Has Been Changed"

    # Step 6.2: Construct plain text alert body
    body_text = (
        f"Hello {username},\n\n"
        f"This is to confirm that the password for your account '{username}' has been successfully changed.\n\n"
        f"If you performed this action, no further steps are required.\n"
        f"If you did NOT change your password, please contact support immediately.\n\n"
        f"Best regards,\nPersonal Finance Security Team"
    )

    # Step 6.3: Construct HTML template alert body
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

    # Step 6.4: Trigger email dispatch
    return send_email(to_email, subject, body_text, body_html)


# Step 7: Dispatch Email Update Verification OTP.
def send_email_update_otp(to_email: str, username: str, otp: str) -> tuple[bool, str]:
    """Send 6-digit OTP code to verify new email address update."""
    subject = f"Verify Your New Email Address OTP: {otp}"

    body_text = (
        f"Hello {username},\n\n"
        f"We received a request to update the email address for account '{username}' to: {to_email}.\n\n"
        f"Your Email Verification OTP is: {otp}\n\n"
        f"This OTP is valid for 5 minutes. Enter this code in the app to confirm your new email.\n\n"
        f"Best regards,\nPersonal Finance Team"
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #ffffff;">
          <h2 style="color: #2b5876; margin-top: 0;">Email Update Verification</h2>
          <p>Hello <strong>{username}</strong>,</p>
          <p>Use the following 6-digit OTP code to confirm your new email address (<strong>{to_email}</strong>):</p>
          <div style="text-align: center; margin: 25px 0;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #2b5876; background-color: #eef2f5; padding: 10px 20px; border-radius: 6px;">{otp}</span>
          </div>
          <p style="color: #e74c3c;"><strong>Note:</strong> This OTP is valid for <strong>5 minutes</strong>.</p>
        </div>
      </body>
    </html>
    """

    return send_email(to_email, subject, body_text, body_html)


# Step 8: Dispatch Monthly Financial Report Email
def send_monthly_report_email(
    to_email: str,
    username: str,
    month: str,
    income_total: float,
    expense_total: float,
    savings_total: float,
    budget_total: float,
) -> tuple[bool, str]:
    """Send beautifully formatted HTML Monthly Financial Report email to user."""
    subject = f"📊 Monthly Financial Report for {month} - Personal Finance"

    rem_budget = budget_total - expense_total
    budget_status = f"Under budget by Rs. {rem_budget:,.2f}" if rem_budget >= 0 else f"OVER budget by Rs. {abs(rem_budget):,.2f}"

    body_text = (
        f"Hello {username},\n\n"
        f"Here is your Personal Financial Report for {month}:\n\n"
        f"Total Income   : Rs. {income_total:,.2f}\n"
        f"Total Expenses : Rs. {expense_total:,.2f}\n"
        f"Monthly Savings: Rs. {savings_total:,.2f}\n"
        f"Budget Summary : {budget_status}\n\n"
        f"Best regards,\nPersonal Finance Team"
    )

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
          <h2 style="color: #1e293b; margin-top: 0; font-size: 22px;">📊 Monthly Financial Report ({month})</h2>
          <p>Hello <strong>{username}</strong>,</p>
          <p>Here is a summary of your financial health for the month of <strong>{month}</strong>:</p>

          <div style="background-color: #f8fafc; padding: 18px; border-radius: 8px; border: 1px solid #cbd5e1; margin: 20px 0;">
            <table style="width: 100%; border-collapse: collapse;">
              <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 10px 0; font-weight: bold; color: #1e293b;">💵 Total Income</td>
                <td style="padding: 10px 0; text-align: right; color: #16a34a; font-weight: bold; font-size: 16px;">Rs. {income_total:,.2f}</td>
              </tr>
              <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 10px 0; font-weight: bold; color: #1e293b;">💸 Total Expenses</td>
                <td style="padding: 10px 0; text-align: right; color: #dc2626; font-weight: bold; font-size: 16px;">Rs. {expense_total:,.2f}</td>
              </tr>
              <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 10px 0; font-weight: bold; color: #1e293b;">📈 Monthly Savings</td>
                <td style="padding: 10px 0; text-align: right; color: #2563eb; font-weight: bold; font-size: 16px;">Rs. {savings_total:,.2f}</td>
              </tr>
              <tr>
                <td style="padding: 10px 0; font-weight: bold; color: #1e293b;">🎯 Budget Status</td>
                <td style="padding: 10px 0; text-align: right; color: #475569; font-weight: bold;">{budget_status}</td>
              </tr>
            </table>
          </div>

          <p style="font-size: 13px; color: #64748b;">Generated automatically by your Personal Finance Management System.</p>
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
          <p style="font-size: 12px; color: #94a3b8; text-align: center;">Personal Finance App &bull; Keep your goals on track</p>
        </div>
      </body>
    </html>
    """

    return send_email(to_email, subject, body_text, body_html)


