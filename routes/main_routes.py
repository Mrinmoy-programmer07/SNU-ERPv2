"""Main routes — dashboard and general pages.

Handles the landing page / dashboard with summary statistics
computed from live Firestore data.
"""

from flask import Blueprint, render_template, flash
from services import firebase_client
from services.student_service import format_student_for_display

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    """Render the dashboard page with summary statistics.

    Fetches all students from Firestore and computes:
    - Total student count
    - Average marks
    - Top scorer (highest marks)
    - Number of unique departments
    - 5 most recently added students
    """
    try:
        raw_students = firebase_client.get_all_students()
        students = [format_student_for_display(s) for s in raw_students]
    except Exception as e:
        flash(f"Could not load dashboard data: {e}", "error")
        students = []

    # Compute stats
    total = len(students)
    avg = 0
    top_scorer = None
    departments = set()

    if total > 0:
        marks_list = [s.get("marks", 0) for s in students]
        avg = round(sum(marks_list) / total, 1)

        # Find top scorer
        top_idx = marks_list.index(max(marks_list))
        top_scorer = students[top_idx]

        # Unique departments
        departments = set(s.get("department", "") for s in students if s.get("department"))

    stats = {
        "total_students": total,
        "average_marks": avg,
        "top_scorer": top_scorer,
        "department_count": len(departments),
    }

    # Recent students — sort by added_on descending, take first 5
    # Since format_student_for_display converts timestamps to strings,
    # we need to sort from raw data
    try:
        sorted_raw = sorted(
            raw_students,
            key=lambda s: s.get("added_on", "") or "",
            reverse=True,
        )
        recent_students = [format_student_for_display(s) for s in sorted_raw[:5]]
    except Exception:
        recent_students = students[:5]

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_students=recent_students,
    )
