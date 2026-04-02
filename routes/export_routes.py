"""Export/Import routes — CSV export and bulk import functionality.

Handles downloading student data as CSV and uploading CSV files
for bulk import into Firestore.
"""

from flask import Blueprint, flash, redirect, url_for

export_bp = Blueprint("export", __name__)


@export_bp.route("/export/csv")
def export_csv():
    """Export all student records as a downloadable CSV file."""
    # Will be implemented in Phase 3
    flash("CSV export functionality coming in Phase 3.", "info")
    return redirect(url_for("students.list_students"))


@export_bp.route("/import", methods=["POST"])
def import_csv():
    """Process an uploaded CSV file for bulk student import."""
    # Will be implemented in Phase 3
    flash("CSV import functionality coming in Phase 3.", "info")
    return redirect(url_for("students.list_students"))
