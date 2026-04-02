"""Student routes — CRUD operations for student records.

Handles add, view all, edit, and delete operations,
each backed by Firestore via the firebase_client service.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services import firebase_client
from services.student_service import (
    validate_student_data,
    format_student_for_display,
    prepare_student_for_save,
)

student_bp = Blueprint("students", __name__)


# ---------------------------------------------------------------------------
# View All Students
# ---------------------------------------------------------------------------

@student_bp.route("/")
def list_students():
    """Render the student list page with all records from Firestore."""
    try:
        raw_students = firebase_client.get_all_students()
        students = [format_student_for_display(s) for s in raw_students]
    except Exception as e:
        flash(f"Could not load students: {e}", "error")
        students = []

    return render_template("students/list.html", students=students)


# ---------------------------------------------------------------------------
# Add Student
# ---------------------------------------------------------------------------

@student_bp.route("/add", methods=["GET"])
def add_student_form():
    """Render the add student form."""
    return render_template("students/add.html")


@student_bp.route("/add", methods=["POST"])
def add_student():
    """Process the add student form submission.

    Validates input server-side, checks for duplicate roll number,
    writes to Firestore, and redirects with success/error feedback.
    """
    form_data = {
        "roll_number": request.form.get("roll_number", ""),
        "name": request.form.get("name", ""),
        "department": request.form.get("department", ""),
        "marks": request.form.get("marks", ""),
        "email": request.form.get("email", ""),
        "phone": request.form.get("phone", ""),
    }

    # Server-side validation
    errors = validate_student_data(form_data, is_edit=False)

    # Check for duplicate roll number
    if "roll_number" not in errors and form_data["roll_number"].strip():
        roll_upper = form_data["roll_number"].strip().upper()
        try:
            if firebase_client.student_exists(roll_upper):
                errors["roll_number"] = f"Roll number '{roll_upper}' already exists."
        except Exception:
            pass  # Firebase not connected — will fail on write anyway

    if errors:
        # Re-render form with errors
        for field, msg in errors.items():
            flash(msg, "error")
        return render_template("students/add.html"), 400

    # Prepare and save
    try:
        clean_data = prepare_student_for_save(form_data)
        roll = firebase_client.add_student(clean_data)

        # Audit log
        try:
            firebase_client.log_action("ADD", roll, f"Added student: {clean_data['name']}")
        except Exception:
            pass  # Non-critical

        flash(f"Student {clean_data['name']} ({roll}) added successfully!", "success")
        return redirect(url_for("students.list_students"))

    except Exception as e:
        flash(f"Failed to add student: {e}", "error")
        return render_template("students/add.html"), 500


# ---------------------------------------------------------------------------
# Edit Student
# ---------------------------------------------------------------------------

@student_bp.route("/edit/<roll>", methods=["GET"])
def edit_student_form(roll):
    """Render the edit student form pre-filled with current data.

    Args:
        roll: The student's roll number (document ID).
    """
    try:
        student = firebase_client.get_student(roll)
    except Exception as e:
        flash(f"Error loading student: {e}", "error")
        return redirect(url_for("students.list_students"))

    if not student:
        flash(f"Student with roll number '{roll}' not found.", "error")
        return redirect(url_for("students.list_students"))

    student = format_student_for_display(student)
    return render_template("students/edit.html", student=student, roll=roll)


@student_bp.route("/edit/<roll>", methods=["POST"])
def edit_student(roll):
    """Process the edit student form submission.

    Validates input, updates document in Firestore,
    automatically refreshes the last_updated timestamp.

    Args:
        roll: The student's roll number (document ID).
    """
    form_data = {
        "name": request.form.get("name", ""),
        "department": request.form.get("department", ""),
        "marks": request.form.get("marks", ""),
        "email": request.form.get("email", ""),
        "phone": request.form.get("phone", ""),
    }

    # Server-side validation (skip roll_number check for edits)
    errors = validate_student_data({**form_data, "roll_number": roll}, is_edit=True)

    if errors:
        for field, msg in errors.items():
            flash(msg, "error")
        # Re-render form with current values
        student = {**form_data, "roll_number": roll}
        return render_template("students/edit.html", student=student, roll=roll), 400

    # Prepare and update
    try:
        clean_data = prepare_student_for_save({**form_data, "roll_number": roll})
        success = firebase_client.update_student(roll, clean_data)

        if success:
            # Audit log
            try:
                firebase_client.log_action("UPDATE", roll, f"Updated student: {clean_data['name']}")
            except Exception:
                pass

            flash(f"Student {clean_data['name']} ({roll}) updated successfully!", "success")
            return redirect(url_for("students.list_students"))
        else:
            flash(f"Student with roll number '{roll}' not found.", "error")
            return redirect(url_for("students.list_students"))

    except Exception as e:
        flash(f"Failed to update student: {e}", "error")
        student = {**form_data, "roll_number": roll}
        return render_template("students/edit.html", student=student, roll=roll), 500


# ---------------------------------------------------------------------------
# Delete Student
# ---------------------------------------------------------------------------

@student_bp.route("/delete/<roll>", methods=["POST"])
def delete_student(roll):
    """Delete a student record from Firestore.

    Args:
        roll: The student's roll number (document ID).
    """
    try:
        # Get student name before deletion for the flash message
        student = firebase_client.get_student(roll)
        student_name = student["name"] if student else roll

        success = firebase_client.delete_student(roll)

        if success:
            # Audit log
            try:
                firebase_client.log_action("DELETE", roll, f"Deleted student: {student_name}")
            except Exception:
                pass

            flash(f"Student {student_name} ({roll}) deleted successfully.", "success")
        else:
            flash(f"Student with roll number '{roll}' not found.", "error")

    except Exception as e:
        flash(f"Failed to delete student: {e}", "error")

    return redirect(url_for("students.list_students"))
