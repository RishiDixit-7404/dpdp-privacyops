from dpdp_scanner.masking import mask_value


def test_email_masking() -> None:
    assert mask_value("rahul.sharma@gmail.com", "email") == "r***********@gmail.com"


def test_phone_masking() -> None:
    assert mask_value("9876543210", "indian_phone") == "98******10"
    assert mask_value("+91 9876543210", "indian_phone") == "+91 98******10"


def test_pan_masking() -> None:
    assert mask_value("ABCDE1234F", "pan") == "ABC********"


def test_aadhaar_masking() -> None:
    assert mask_value("1234 5678 9012", "aadhaar") == "**** **** 9012"


def test_upi_masking() -> None:
    assert mask_value("rahul@upi", "upi_id") == "r****@upi"


def test_secret_masking() -> None:
    assert mask_value("Bearer abcdefghijk", "authentication_secret") == "Bearer ab********"

