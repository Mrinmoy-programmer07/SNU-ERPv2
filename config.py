"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Flask configuration class."""

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-fallback-secret-key")

    # Firebase configuration
    FIREBASE_CREDENTIALS = os.getenv(
        "FIREBASE_CREDENTIALS",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "firebase-key.json"),
    )

    # Firestore collection names
    STUDENTS_COLLECTION = "students"
    AUDIT_LOG_COLLECTION = "audit_log"

    # Valid departments
    DEPARTMENTS = ["CSE", "ECE", "ME", "EE", "CE"]
