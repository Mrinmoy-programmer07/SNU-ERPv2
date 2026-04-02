from app import create_app
import io

app = create_app()
app.config['TESTING'] = True
client = app.test_client()

csv_data = """Roll Number,Name,Department,Marks,Email,Phone
MECH001,Amit Kumar,ME,78,amit@example.com,9876543211
CIVIL002,Sneha Reddy,CE,88,sneha@example.com,9876543212
"""

data = {
    'csv_file': (io.BytesIO(csv_data.encode('utf-8')), 'test.csv')
}

with client:
    response = client.post('/import', data=data, content_type='multipart/form-data')
    print("Redirect to:", response.location)
    # Check flash messages
    with client.session_transaction() as session:
        flashes = session.get('_flashes', [])
        print("Flashes:", flashes)
