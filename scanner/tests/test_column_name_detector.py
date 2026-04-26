from dpdp_scanner.detectors.column_name_detector import ColumnNameDetector


def types_for(column_name: str) -> set[str]:
    return {detection.pii_type for detection in ColumnNameDetector().detect(column_name)}


def test_column_name_classification() -> None:
    assert "email" in types_for("email_address")
    assert "indian_phone" in types_for("parent_phone")
    assert "pan" in types_for("pan_number")
    assert "aadhaar" in types_for("aadhar_number")
    assert "upi_id" in types_for("vpa")
    assert "date_of_birth" in types_for("birth_date")
    assert "person_name" in types_for("full_name")
    assert "address" in types_for("postal_code")
    assert "student_or_child_data" in types_for("guardian_name")
    assert "health_data" in types_for("diagnosis")
    assert "employment_data" in types_for("employee_id")
    assert "financial_data" in types_for("bank_account")
    assert "authentication_secret" in types_for("api_key")
    assert "free_text_possible_pii" in types_for("ticket_body")

