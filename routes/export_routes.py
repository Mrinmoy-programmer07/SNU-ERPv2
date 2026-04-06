"""Export/Import routes — CSV export and bulk import functionality.

Handles downloading student data as CSV and uploading CSV files
for bulk import into Firestore.
"""

import csv
import io
from flask import Blueprint, flash, redirect, url_for, Response, request
from services import firebase_client
import datetime
from services.student_service import validate_student_data, prepare_student_for_save

export_bp = Blueprint("export", __name__)


@export_bp.route("/export/csv")
def export_csv():
    """Export all student records as a downloadable CSV file."""
    try:
        students = firebase_client.get_all_students()
        
        # Create an in-memory string buffer
        si = io.StringIO()
        
        # Define CSV headers
        fieldnames = ["Roll Number", "Name", "Department", "Year", "Marks", "Email", "Phone", "Added On", "Last Updated"]
        writer = csv.DictWriter(si, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for s in students:
            writer.writerow({
                "Roll Number": s.get("roll_number", ""),
                "Name": s.get("name", ""),
                "Department": s.get("department", ""),
                "Year": s.get("year", 1),
                "Marks": s.get("marks", ""),
                "Email": s.get("email", ""),
                "Phone": s.get("phone", ""),
                "Added On": s.get("added_on", ""),
                "Last Updated": s.get("last_updated", "")
            })

        output = si.getvalue()
        
        # Determine filename with current date
        filename = f"students_export_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
        
        # Return response with CSV file
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    except Exception as e:
        flash(f"Failed to export CSV: {e}", "error")
        return redirect(url_for("students.list_students"))


@export_bp.route("/import", methods=["POST"])
def import_csv():
    """Process an uploaded CSV file for bulk student import."""
    if 'csv_file' not in request.files:
        flash('No file uploaded.', 'error')
        return redirect(url_for('students.list_students'))
        
    file = request.files['csv_file']
    
    if file.filename == '':
        flash('No selected file.', 'error')
        return redirect(url_for('students.list_students'))
        
    if not file.filename.endswith('.csv'):
        flash('Invalid file format. Please upload a CSV file.', 'error')
        return redirect(url_for('students.list_students'))

    try:
        # Read the file content
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        success_count = 0
        error_count = 0
        
        # Expected column names in CSV (can be flexible, but these are from our export)
        # Roll Number, Name, Department, Year, Marks, Email, Phone
        # Map them if possible, or fall back to lowercase snake_case
        
        for row in csv_input:
            # Map columns defensively in case headers are slightly different
            form_data = {
                "roll_number": row.get("Roll Number", row.get("roll_number", "")),
                "name": row.get("Name", row.get("name", "")),
                "department": row.get("Department", row.get("department", "")),
                "year": row.get("Year", row.get("year", 1)),
                "marks": row.get("Marks", row.get("marks", "")),
                "email": row.get("Email", row.get("email", "")),
                "phone": row.get("Phone", row.get("phone", ""))
            }
            
            # Skip empty rows
            if not form_data["roll_number"] and not form_data["name"]:
                continue
                
            errors = validate_student_data(form_data, is_edit=False)
            
            # Check for duplicate roll number
            if "roll_number" not in errors and form_data["roll_number"].strip():
                roll_upper = form_data["roll_number"].strip().upper()
                try:
                    if firebase_client.student_exists(roll_upper):
                        errors["roll_number"] = f"Roll number '{roll_upper}' already exists."
                except Exception:
                    pass
            
            if not errors:
                try:
                    clean_data = prepare_student_for_save(form_data)
                    roll = firebase_client.add_student(clean_data)
                    
                    try:
                        firebase_client.log_action("IMPORT", roll, f"Imported student via CSV: {clean_data['name']}")
                    except Exception:
                        pass
                    
                    success_count += 1
                except Exception:
                    error_count += 1
            else:
                error_count += 1
                
        if success_count > 0:
            msg = f"Successfully imported {success_count} students."
            if error_count > 0:
                msg += f" ({error_count} rows failed validation or were duplicates)."
            flash(msg, "success")
        elif error_count > 0:
            flash(f"Failed to import any students. {error_count} rows failed validation.", "error")
        else:
            flash("No data found in the CSV file.", "info")
            
    except Exception as e:
        flash(f"Error processing CSV file: {e}", "error")
        
    return redirect(url_for("students.list_students"))
