"""Firebase Admin SDK wrapper for Firestore operations.

Provides initialization, connection management, and CRUD operations
for the students collection in Firestore.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone


# Module-level state
_app = None
_db = None


def initialize_firebase(credentials_path: str) -> None:
    """Initialize Firebase Admin SDK with service account credentials.

    Args:
        credentials_path: Path to the Firebase service account JSON key file.

    Raises:
        FileNotFoundError: If the credentials file does not exist.
        ValueError: If the credentials file is invalid.
    """
    global _app, _db

    if _app is not None:
        return  # Already initialized

    cred = credentials.Certificate(credentials_path)
    _app = firebase_admin.initialize_app(cred)
    _db = firestore.client()


def get_db():
    """Return the Firestore client instance.

    Returns:
        google.cloud.firestore.Client: The Firestore client.

    Raises:
        RuntimeError: If Firebase has not been initialized.
    """
    if _db is None:
        raise RuntimeError(
            "Firebase has not been initialized. Call initialize_firebase() first."
        )
    return _db


# ---------------------------------------------------------------------------
# Students Collection CRUD
# ---------------------------------------------------------------------------

STUDENTS_COLLECTION = "students"


def get_all_students() -> list[dict]:
    """Retrieve all student documents from Firestore.

    Returns:
        A list of dicts, each containing the student document data
        plus an 'id' field set to the document ID (roll_number).
    """
    db = get_db()
    docs = db.collection(STUDENTS_COLLECTION).stream()

    students = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        students.append(data)

    return students


def get_student(roll_number: str) -> dict | None:
    """Get a single student document by roll number.

    Args:
        roll_number: The student's roll number (used as document ID or field).

    Returns:
        A dict of the student's data with 'id' field, or None if not found.
    """
    db = get_db()
    doc_ref = db.collection(STUDENTS_COLLECTION).document(roll_number)
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    # Fallback: query by roll_number field
    docs = db.collection(STUDENTS_COLLECTION).where("roll_number", "==", roll_number).limit(1).stream()
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        return data

    return None


def add_student(data: dict) -> str:
    """Add a new student document to Firestore.

    Uses the roll_number as the document ID for O(1) lookups.
    Automatically adds an 'added_on' timestamp.

    Args:
        data: A dict containing student fields (must include 'roll_number').

    Returns:
        The roll_number (document ID) of the created document.

    Raises:
        ValueError: If roll_number is missing from data.
    """
    if "roll_number" not in data or not data["roll_number"]:
        raise ValueError("roll_number is required.")

    roll_number = data["roll_number"].strip().upper()
    student_data = {
        "roll_number": roll_number,
        "name": data.get("name", "").strip(),
        "department": data.get("department", "").strip().upper(),
        "marks": int(data.get("marks", 0)),
        "email": data.get("email", "").strip().lower(),
        "phone": data.get("phone", "").strip(),
        "added_on": firestore.SERVER_TIMESTAMP,
        "last_updated": firestore.SERVER_TIMESTAMP,
    }

    db = get_db()
    db.collection(STUDENTS_COLLECTION).document(roll_number).set(student_data)

    return roll_number


def update_student(roll_number: str, data: dict) -> bool:
    """Update an existing student document in Firestore.

    Automatically updates the 'last_updated' timestamp.

    Args:
        roll_number: The student's roll number (document ID or field).
        data: A dict of fields to update.

    Returns:
        True if the document was found and updated, False otherwise.
    """
    db = get_db()
    doc_ref = db.collection(STUDENTS_COLLECTION).document(roll_number)

    if not doc_ref.get().exists:
        # Fallback to query by roll_number field
        docs = list(db.collection(STUDENTS_COLLECTION).where("roll_number", "==", roll_number).limit(1).stream())
        if not docs:
            return False
        doc_ref = docs[0].reference

    update_data = {}
    if "name" in data:
        update_data["name"] = data["name"].strip()
    if "department" in data:
        update_data["department"] = data["department"].strip().upper()
    if "marks" in data:
        update_data["marks"] = int(data["marks"])
    if "email" in data:
        update_data["email"] = data["email"].strip().lower()
    if "phone" in data:
        update_data["phone"] = data["phone"].strip()

    update_data["last_updated"] = firestore.SERVER_TIMESTAMP

    doc_ref.update(update_data)
    return True


def delete_student(roll_number: str) -> bool:
    """Delete a student document from Firestore.

    Args:
        roll_number: The student's roll number (document ID or field).

    Returns:
        True if the document existed and was deleted, False otherwise.
    """
    db = get_db()
    doc_ref = db.collection(STUDENTS_COLLECTION).document(roll_number)

    if not doc_ref.get().exists:
        # Fallback to query by roll_number field
        docs = list(db.collection(STUDENTS_COLLECTION).where("roll_number", "==", roll_number).limit(1).stream())
        if not docs:
            return False
        doc_ref = docs[0].reference

    doc_ref.delete()
    return True


def student_exists(roll_number: str) -> bool:
    """Check if a student document exists in Firestore.

    Args:
        roll_number: The student's roll number (document ID or field).

    Returns:
        True if the document exists, False otherwise.
    """
    db = get_db()
    doc = db.collection(STUDENTS_COLLECTION).document(roll_number).get()
    if doc.exists:
        return True
    
    # Fallback to query by roll_number field
    docs = list(db.collection(STUDENTS_COLLECTION).where("roll_number", "==", roll_number).limit(1).stream())
    return len(docs) > 0


# ---------------------------------------------------------------------------
# Audit Log (Stretch Goal)
# ---------------------------------------------------------------------------

AUDIT_LOG_COLLECTION = "audit_log"


def log_action(action: str, roll_number: str, details: str = "") -> None:
    """Write an entry to the audit_log collection.

    Args:
        action: The action type (ADD, UPDATE, DELETE).
        roll_number: The affected student's roll number.
        details: Optional description of the change.
    """
    db = get_db()
    db.collection(AUDIT_LOG_COLLECTION).add(
        {
            "timestamp": firestore.SERVER_TIMESTAMP,
            "action": action,
            "roll_number": roll_number,
            "details": details,
        }
    )
