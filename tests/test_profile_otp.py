import pytest
from auth import UserManager


def test_profile_email_otp_workflow(temp_data_dir):
    manager = UserManager()
    # Create test user
    ok_signup, msg_signup = manager.signup("otptestuser", "password123", "OTP Test", "old@example.com", "+919876543210")
    assert ok_signup is True

    # Step 1: Request Email Update OTP
    ok, msg = manager.request_email_change_otp("otptestuser", "new_email@example.com")
    assert ok is True
    assert "OTP sent to new_email@example.com" in msg
    assert "otptestuser" in manager.profile_otps

    otp_entry = manager.profile_otps["otptestuser"]
    assert otp_entry["type"] == "email"
    assert otp_entry["value"] == "new_email@example.com"
    otp_code = otp_entry["otp"]

    # Step 2: Try invalid OTP
    bad_ok, bad_msg = manager.verify_profile_otp_and_update("otptestuser", "000000")
    assert bad_ok is False
    assert "Invalid OTP code" in bad_msg

    # Step 3: Verify with correct OTP
    good_ok, good_msg = manager.verify_profile_otp_and_update("otptestuser", otp_code)
    assert good_ok is True
    assert "updated to 'new_email@example.com'" in good_msg

    # Check users dictionary
    assert manager.users["otptestuser"]["email"] == "new_email@example.com"


def test_profile_phone_otp_workflow(temp_data_dir):
    manager = UserManager()
    # Create test user
    ok_signup, msg_signup = manager.signup("phonetestuser", "password123", "Phone Test", "phone@example.com", "+919876543210")
    assert ok_signup is True

    # Step 1: Request Phone Update OTP
    ok, msg, otp_code, wa_link = manager.request_phone_change_otp("phonetestuser", "+919123456789")
    assert ok is True
    assert "api.whatsapp.com/send" in wa_link
    assert "phonetestuser" in manager.profile_otps

    # Step 2: Verify with correct OTP
    good_ok, good_msg = manager.verify_profile_otp_and_update("phonetestuser", otp_code)
    assert good_ok is True
    assert "updated to '+919123456789'" in good_msg

    # Check users dictionary
    assert manager.users["phonetestuser"]["phone"] == "+919123456789"
