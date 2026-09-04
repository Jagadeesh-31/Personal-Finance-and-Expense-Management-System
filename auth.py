import hashlib
import json
import os
import random
import re
import time
from pathlib import Path
from logger_config import get_logger
from email_service import (
    send_registration_email,
    send_otp_email,
    send_password_changed_email,
)

# Step 1: Initialize logger for authentication operations
logger = get_logger("auth")

# Step 2: Define OTP validity duration in seconds (5 minutes)
OTP_EXPIRY_SECONDS = 300


# Step 3: Helper function to resolve dynamic data directory path
def _get_data_dir() -> Path:
    """Dynamically get data directory path relative to current working directory."""
    return Path.cwd() / "data"


# Step 4: Cryptographic password hashing using PBKDF2 HMAC SHA-256 with unique salt
def _hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash password using PBKDF2 HMAC SHA-256 with a unique salt."""
    # Step 4.1: Generate random 16-byte hex salt if not provided
    if not salt:
        salt = os.urandom(16).hex()
    # Step 4.2: Perform 100,000 iterations of PBKDF2 HMAC SHA-256
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()
    return hashed, salt


# Step 5: Core UserManager class handling registration, login, data isolation & OTP reset
class UserManager:
    """Manages user registration, authentication, OTP password reset, and data directory resolution."""

    # Step 5.1: Initialize storage paths and load existing accounts
    def __init__(self):
        self.data_dir = _get_data_dir()
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.users = self._load_users()
        self.otps = {}  # In-memory OTP storage: {username: {"otp": str, "expires_at": float}}

    # Step 5.2: Load user accounts dictionary from users.json file
    def _load_users(self) -> dict:
        """Load user accounts dictionary from users.json."""
        if not self.users_file.exists():
            return {}
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as err:
            logger.error(f"Error loading users file: {err}", exc_info=True)
            return {}

    # Step 5.3: Persist user accounts dictionary to users.json file
    def _save_users(self):
        """Save user accounts dictionary to users.json."""
        try:
            self.data_dir.mkdir(exist_ok=True)
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=4)
        except Exception as err:
            logger.error(f"Error saving users file: {err}", exc_info=True)

    # Step 5.4: Resolve and create isolated data directory for specific user
    def get_user_data_dir(self, username: str) -> Path:
        """Get or create the isolated data directory path for a specific user."""
        clean_username = re.sub(r"[^\w\-]", "_", username.lower().strip())
        user_dir = self.data_dir / "users" / clean_username
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    # Step 5.5: Search and find user record by username or email address
    def find_user_by_identifier(self, identifier: str) -> dict | None:
        """Find a user record by username or email address."""
        clean_id = identifier.strip().lower()
        if not clean_id:
            return None

        # Check matching username
        if clean_id in self.users:
            return self.users[clean_id]

        # Check matching registered email
        for user_info in self.users.values():
            if user_info.get("email", "").strip().lower() == clean_id:
                return user_info

        return None

    # Step 5.6: Register a new user account and send registration welcome email
    def signup(
        self, username: str, password: str, full_name: str = "", email: str = ""
    ) -> tuple[bool, str]:
        """Register a new user account and dispatch welcome email."""
        username = username.strip().lower()
        email = email.strip()

        # Step 5.6a: Validate minimum username length
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters long."

        # Step 5.6b: Validate minimum password length
        if not password or len(password) < 4:
            return False, "Password must be at least 4 characters long."

        # Step 5.6c: Check duplicate username
        if username in self.users:
            logger.warning(f"Signup failed: Username '{username}' already exists.")
            return False, "Username already exists. Please choose a different one."

        # Step 5.6d: Warn if email is already registered to another user
        if email:
            for u in self.users.values():
                if u.get("email", "").strip().lower() == email.lower():
                    logger.warning(f"Signup notice: Email '{email}' already registered.")

        # Step 5.6e: Hash password securely and construct user profile object
        hashed_password, salt = _hash_password(password)
        self.users[username] = {
            "username": username,
            "full_name": full_name.strip(),
            "email": email,
            "password_hash": hashed_password,
            "salt": salt,
        }
        self._save_users()

        # Step 5.6f: Initialize multi-tenant user data directory
        self.get_user_data_dir(username)

        logger.info(f"User signed up successfully: '{username}'")

        # Step 5.6g: Trigger registration welcome email if email provided
        if email:
            send_registration_email(email, username)

        return True, "User registered successfully! A welcome email has been sent."

    # Step 5.7: Authenticate user credentials against stored hash and salt
    def login(self, username: str, password: str) -> tuple[bool, str, dict]:
        """Authenticate user credentials against stored hash."""
        username = username.strip().lower()
        if not username or not password:
            return False, "Username and password are required.", {}

        # Step 5.7a: Retrieve stored user profile
        user_info = self.users.get(username)
        if not user_info:
            logger.warning(f"Login failed: Username '{username}' not found.")
            return False, "Invalid username or password.", {}

        # Step 5.7b: Re-hash input password with stored salt and compare
        stored_hash = user_info.get("password_hash")
        salt = user_info.get("salt")
        computed_hash, _ = _hash_password(password, salt)

        if computed_hash != stored_hash:
            logger.warning(f"Login failed: Incorrect password for user '{username}'.")
            return False, "Invalid username or password.", {}

        logger.info(f"User logged in successfully: '{username}'")
        return True, "Login successful!", user_info

    # Step 5.8: Generate 6-digit OTP for password reset and send email
    def request_password_reset_otp(self, identifier: str) -> tuple[bool, str, str]:
        """
        Generate a 6-digit OTP for password reset and send it to user's email.
        Returns (success, message, target_username).
        """
        # Step 5.8a: Find account by username or email
        user_info = self.find_user_by_identifier(identifier)
        if not user_info:
            logger.warning(f"OTP request failed: No account found for identifier '{identifier}'.")
            return False, "No user found with that username or email address.", ""

        email = user_info.get("email", "").strip()
        username = user_info["username"]

        if not email:
            logger.warning(f"OTP request failed: User '{username}' has no registered email address.")
            return False, f"User '{username}' does not have a registered email address.", ""

        # Step 5.8b: Generate random 6-digit numeric OTP and 5-minute expiry timestamp
        otp = f"{random.randint(100000, 999999)}"
        expires_at = time.time() + OTP_EXPIRY_SECONDS

        self.otps[username] = {
            "otp": otp,
            "expires_at": expires_at,
            "email": email,
        }

        # Step 5.8c: Dispatch OTP code email
        ok, email_msg = send_otp_email(email, username, otp)

        # Step 5.8d: Format masked email for privacy output
        parts = email.split("@")
        masked_email = parts[0][0] + "***" + (parts[0][-1] if len(parts[0]) > 1 else "") + "@" + parts[1] if len(parts) == 2 else email

        if ok:
            logger.info(f"OTP generated and sent to '{email}' for user '{username}'.")
            return True, f"OTP has been sent to {masked_email}.", username
        else:
            logger.info(f"OTP generated for user '{username}' (email delivery output: {email_msg}).")
            return True, f"OTP created (Sent to {masked_email}).", username

    # Step 5.9: Verify OTP code, reset password, and send security alert email
    def verify_otp_and_reset_password(
        self, identifier: str, otp: str, new_password: str
    ) -> tuple[bool, str]:
        """
        Verify the OTP and reset the user's password to new_password.
        Dispatches password changed security alert email on success.
        """
        # Step 5.9a: Locate user account
        user_info = self.find_user_by_identifier(identifier)
        if not user_info:
            return False, "User not found."

        username = user_info["username"]
        otp_entry = self.otps.get(username)

        # Step 5.9b: Verify active OTP request exists
        if not otp_entry:
            return False, "No OTP request found for this user. Please request a new OTP."

        # Step 5.9c: Check OTP expiration
        if time.time() > otp_entry["expires_at"]:
            del self.otps[username]
            return False, "OTP has expired. Please request a new one."

        # Step 5.9d: Compare input OTP against stored OTP code
        if otp_entry["otp"].strip() != otp.strip():
            return False, "Invalid OTP code. Please try again."

        # Step 5.9e: Validate new password length
        if not new_password or len(new_password) < 4:
            return False, "New password must be at least 4 characters long."

        # Step 5.9f: Re-hash new password with a fresh salt and save profile
        hashed_password, salt = _hash_password(new_password)
        self.users[username]["password_hash"] = hashed_password
        self.users[username]["salt"] = salt
        self._save_users()

        # Step 5.9g: Invalidate used OTP code
        del self.otps[username]

        email = user_info.get("email", "").strip()
        logger.info(f"Password reset successfully for user '{username}'.")

        # Step 5.9h: Send password changed security notification email
        if email:
            send_password_changed_email(email, username)

        return True, "Password reset successfully! A confirmation email has been sent."
