import pytest
import time
from unittest.mock import patch
from auth import UserManager, _hash_password


@pytest.fixture(autouse=True)
def mock_email_service():
    """Mock email service functions during test runs for instant execution."""
    with patch("auth.send_registration_email", return_value=(True, "Mocked email sent")) as m_reg, \
         patch("auth.send_otp_email", return_value=(True, "Mocked OTP sent")) as m_otp, \
         patch("auth.send_password_changed_email", return_value=(True, "Mocked password alert sent")) as m_pwd:
        yield {
            "send_registration_email": m_reg,
            "send_otp_email": m_otp,
            "send_password_changed_email": m_pwd,
        }


def test_password_hashing():
    pwd = "SecretPassword123"
    hash1, salt1 = _hash_password(pwd)
    assert len(hash1) == 64
    assert len(salt1) == 32

    # Verifying same password with same salt produces same hash
    hash2, _ = _hash_password(pwd, salt1)
    assert hash1 == hash2


def test_user_signup_and_login(temp_data_dir, mock_email_service):
    auth = UserManager()

    # Successful Signup
    success, msg = auth.signup("testuser", "pass1234", "Test User", "testuser@example.com")
    assert success is True
    assert "registered successfully" in msg.lower()

    # Verify registration welcome email was triggered
    mock_email_service["send_registration_email"].assert_called_once_with("testuser@example.com", "testuser")

    # Attempt Duplicate Username Signup
    success2, msg2 = auth.signup("testuser", "anotherpass", "Test Copy", "test2@example.com")
    assert success2 is False
    assert "already exists" in msg2.lower()

    # Successful Login
    ok, log_msg, info = auth.login("testuser", "pass1234")
    assert ok is True
    assert info["full_name"] == "Test User"
    assert info["email"] == "testuser@example.com"

    # Failed Login with Incorrect Password
    ok_fail, fail_msg, _ = auth.login("testuser", "wrongpass")
    assert ok_fail is False
    assert "invalid username or password" in fail_msg.lower()

    # Failed Login with Non-Existent User
    ok_no_user, no_user_msg, _ = auth.login("nobody", "pass1234")
    assert ok_no_user is False
    assert "invalid username or password" in no_user_msg.lower()


def test_user_data_dir_creation(temp_data_dir):
    auth = UserManager()
    user_dir = auth.get_user_data_dir("alice")
    assert user_dir.exists()
    assert "alice" in str(user_dir)


def test_forgot_password_otp_and_reset(temp_data_dir, mock_email_service):
    auth = UserManager()
    auth.signup("resetuser", "oldpass123", "Reset User", "reset@example.com")

    # Request OTP by username
    ok, msg, target_user = auth.request_password_reset_otp("resetuser")
    assert ok is True
    assert target_user == "resetuser"
    assert "sent to" in msg.lower() or "created" in msg.lower()

    # Verify OTP was stored and sent via email
    assert "resetuser" in auth.otps
    valid_otp = auth.otps["resetuser"]["otp"]
    assert len(valid_otp) == 6
    mock_email_service["send_otp_email"].assert_called_once_with("reset@example.com", "resetuser", valid_otp)

    # Attempt Reset with Invalid OTP
    bad_ok, bad_msg = auth.verify_otp_and_reset_password("resetuser", "000000", "newpass123")
    assert bad_ok is False
    assert "invalid otp" in bad_msg.lower()

    # Attempt Reset with Valid OTP but short new password
    short_ok, short_msg = auth.verify_otp_and_reset_password("resetuser", valid_otp, "123")
    assert short_ok is False
    assert "at least 4 characters" in short_msg.lower()

    # Successful Password Reset
    res_ok, res_msg = auth.verify_otp_and_reset_password("resetuser", valid_otp, "newpass123")
    assert res_ok is True
    assert "password reset successfully" in res_msg.lower()

    # Verify password changed notification email was triggered
    mock_email_service["send_password_changed_email"].assert_called_once_with("reset@example.com", "resetuser")

    # Login with old password should fail
    old_login, _, _ = auth.login("resetuser", "oldpass123")
    assert old_login is False

    # Login with new password should succeed
    new_login, _, _ = auth.login("resetuser", "newpass123")
    assert new_login is True


def test_otp_expiration(temp_data_dir):
    auth = UserManager()
    auth.signup("expuser", "pass1234", "Expiry User", "exp@example.com")

    auth.request_password_reset_otp("expuser")
    otp = auth.otps["expuser"]["otp"]

    # Manually expire the OTP
    auth.otps["expuser"]["expires_at"] = time.time() - 10

    # Reset attempt with expired OTP should fail
    exp_ok, exp_msg = auth.verify_otp_and_reset_password("expuser", otp, "brandnewpass")
    assert exp_ok is False
    assert "expired" in exp_msg.lower()


def test_profile_picture_upload(temp_data_dir):
    auth = UserManager()
    auth.signup("picuser", "pass1234", "Pic User", "pic@example.com")

    # Mock image bytes (1x1 fake PNG byte sequence)
    fake_png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    ok, msg, rel_path = auth.save_profile_picture("picuser", fake_png_bytes, file_extension=".png")

    assert ok is True
    assert "updated successfully" in msg.lower()
    assert "profile_pic.png" in rel_path

    # Verify user record updated with profile_pic path
    user_info = auth.users.get("picuser")
    assert user_info["profile_pic"] == rel_path


def test_signup_otp_workflow(temp_data_dir, mock_email_service):
    auth = UserManager()

    with patch("auth.send_signup_otp_email", return_value=(True, "Mocked signup OTP sent")) as m_signup_otp:
        # Step 1: Request Signup OTP
        ok, msg = auth.request_signup_otp("newuser", "securepass123", "New User", "newuser@example.com", "+919876543210")
        assert ok is True
        assert "verification otp sent" in msg.lower()

        assert "newuser" in auth.signup_otps
        otp_code = auth.signup_otps["newuser"]["otp"]
        m_signup_otp.assert_called_once_with("newuser@example.com", "newuser", otp_code)

        # Step 2: Attempt verification with invalid OTP
        bad_ok, bad_msg = auth.verify_signup_otp_and_create_account("newuser", "000000")
        assert bad_ok is False
        assert "invalid otp" in bad_msg.lower()

        # Step 3: Verify with valid OTP
        good_ok, good_msg = auth.verify_signup_otp_and_create_account("newuser", otp_code)
        assert good_ok is True
        assert "account successfully verified" in good_msg.lower()

        # Verify user is created in system and can log in
        assert "newuser" in auth.users
        log_ok, _, user_info = auth.login("newuser", "securepass123")
        assert log_ok is True
        assert user_info["email"] == "newuser@example.com"


