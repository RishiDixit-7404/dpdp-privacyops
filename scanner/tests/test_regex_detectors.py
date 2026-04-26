from dpdp_scanner.detectors.regex_detectors import RegexValueDetector


def detected_types(value: str, column_name: str | None = None) -> set[str]:
    detector = RegexValueDetector()
    return {detection.pii_type for detection in detector.detect(value, column_name=column_name)}


def test_email_detection() -> None:
    assert "email" in detected_types("rahul.sharma@example.com")


def test_indian_phone_detection() -> None:
    assert "indian_phone" in detected_types("+91 9876543210")
    assert "indian_phone" in detected_types("919876543210")


def test_pan_detection() -> None:
    assert "pan" in detected_types("ABCDE1234F")


def test_aadhaar_detection() -> None:
    assert "aadhaar" in detected_types("1234 5678 9012")
    assert "aadhaar" in detected_types("123456789012")
    assert "aadhaar" not in detected_types("919876543210")


def test_upi_detection() -> None:
    assert "upi_id" in detected_types("rahul@upi")
    assert "upi_id" not in detected_types("rahul.sharma@example.com")


def test_dob_detection_requires_column_context() -> None:
    assert "date_of_birth" in detected_types("1998-04-15", column_name="dob")
    assert "date_of_birth" not in detected_types("1998-04-15", column_name="created_at")
