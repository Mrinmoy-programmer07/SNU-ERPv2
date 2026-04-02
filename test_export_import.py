import requests
from io import StringIO
import csv

BASE_URL = 'http://127.0.0.1:5000'

def test_export():
    r = requests.get(f"{BASE_URL}/export/csv")
    print(f"Export status: {r.status_code}")
    print("Content-Disposition:", r.headers.get("Content-Disposition"))
    print("CSV Content Snippet:")
    print(r.text[:200])
    return r.text

def test_import():
    csv_data = """Roll Number,Name,Department,Marks,Email,Phone
MECH001,Amit Kumar,MECH,78,amit@example.com,9876543211
CIVIL002,Sneha Reddy,CIVIL,88,sneha@example.com,9876543212
"""
    files = {'csv_file': ('test_import.csv', StringIO(csv_data), 'text/csv')}
    r = requests.post(f"{BASE_URL}/import", files=files, allow_redirects=False)
    print(f"Import redirect status: {r.status_code}")
    headers = str(r.headers)
    print("Headers snippet:", headers[:300])

if __name__ == "__main__":
    print("--- Testing Export ---")
    export_content = test_export()
    print("\n--- Testing Import ---")
    test_import()
