"""Student service — business logic layer.

Provides validation, formatting, and data preparation for student records.
Sits between the routes and the firebase_client data access layer.
"""

import re
from datetime import datetime, timezone


def validate_student_data(data: dict, is_edit: bool = False) -> dict:
    """Validate all student form fields.

    Args:
        data: A dict containing form field values.
        is_edit: If True, skips roll_number uniqueness check (roll_number is immutable).

    Returns:
        A dict of field → error message. Empty dict means valid.
    """
    errors = {}

    # Roll number — required, alphanumeric
    roll = data.get("roll_number", "").strip()
    if not is_edit:
        if not roll:
            errors["roll_number"] = "Roll number is required."
        elif not re.match(r"^[A-Za-z0-9]+$", roll):
            errors["roll_number"] = "Roll number must be alphanumeric (letters and numbers only)."

    # Name — required
    name = data.get("name", "").strip()
    if not name:
        errors["name"] = "Student name is required."
    elif len(name) < 2:
        errors["name"] = "Name must be at least 2 characters."
    elif len(name) > 100:
        errors["name"] = "Name must be 100 characters or fewer."

    # Department — required, must be a valid value
    department = data.get("department", "").strip()
    valid_departments = ["CSE", "ECE", "ME", "EE", "CE"]
    if not department:
        errors["department"] = "Department is required."
    elif department.upper() not in valid_departments:
        errors["department"] = f"Department must be one of: {', '.join(valid_departments)}."

    # Marks — required, 0–100
    marks_raw = data.get("marks", "").strip() if isinstance(data.get("marks"), str) else data.get("marks")
    if marks_raw == "" or marks_raw is None:
        errors["marks"] = "Marks are required."
    else:
        try:
            marks = int(marks_raw)
            if marks < 0 or marks > 100:
                errors["marks"] = "Marks must be between 0 and 100."
        except (ValueError, TypeError):
            errors["marks"] = "Marks must be a valid number."

    # Email — optional, but validate format if provided
    email = data.get("email", "").strip()
    if email:
        email_pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            errors["email"] = "Please enter a valid email address."

    # Phone — optional, but validate format if provided
    phone = data.get("phone", "").strip()
    if phone:
        digits_only = re.sub(r"[\s\-\(\)\+]", "", phone)
        if not digits_only.isdigit() or len(digits_only) < 10 or len(digits_only) > 15:
            errors["phone"] = "Phone number must be 10–15 digits."

    return errors


def format_student_for_display(student: dict) -> dict:
    """Format a Firestore student document for template rendering.

    Converts timestamps to human-readable strings and ensures
    all expected fields exist.

    Args:
        student: Raw student dict from Firestore.

    Returns:
        A new dict with formatted values.
    """
    formatted = {
        "id": student.get("id", ""),
        "roll_number": student.get("roll_number", ""),
        "name": student.get("name", ""),
        "department": student.get("department", ""),
        "marks": student.get("marks", 0),
        "email": student.get("email", ""),
        "phone": student.get("phone", ""),
    }

    # Format timestamps
    added_on = student.get("added_on")
    if added_on:
        if hasattr(added_on, "strftime"):
            formatted["added_on"] = added_on.strftime("%b %d, %Y %I:%M %p")
        else:
            formatted["added_on"] = str(added_on)
    else:
        formatted["added_on"] = "—"

    last_updated = student.get("last_updated")
    if last_updated:
        if hasattr(last_updated, "strftime"):
            formatted["last_updated"] = last_updated.strftime("%b %d, %Y %I:%M %p")
        else:
            formatted["last_updated"] = str(last_updated)
    else:
        formatted["last_updated"] = "—"

    return formatted


def prepare_student_for_save(form_data: dict) -> dict:
    """Clean and prepare form data for writing to Firestore.

    Strips whitespace, normalizes casing, and structures data
    for the firebase_client.add_student() / update_student() calls.

    Args:
        form_data: Raw form data dict (from request.form).

    Returns:
        A cleaned dict ready for Firestore.
    """
    return {
        "roll_number": form_data.get("roll_number", "").strip().upper(),
        "name": form_data.get("name", "").strip().title(),
        "department": form_data.get("department", "").strip().upper(),
        "marks": int(form_data.get("marks", 0)),
        "email": form_data.get("email", "").strip().lower(),
        "phone": form_data.get("phone", "").strip(),
    }
