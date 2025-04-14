import os
import pytest
import socket

# Set environment variables before importing the app module
os.environ['STATEFUL'] = 'true'
os.environ['uri'] = 'sqlite:///:memory:'  # Use an in-memory SQLite database for testing
os.environ['APP_COLOR'] = 'blue'  # Force a valid color

from app import app as flask_app  # Import after setting environment variables

@pytest.fixture
def client(tmp_path):
    # Initialize the database
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['uri']
    flask_app.config['TESTING'] = True
    with flask_app.app_context():
        from app import db
        db.create_all()

    with flask_app.test_client() as client:
        yield client

    # Cleanup after tests
    with flask_app.app_context():
        db.drop_all()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.data == b"OK"


def test_homepage_stateful_mode(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello from" in response.data
    assert b"Write a message" in response.data  # Check for the form


def test_message_submission(client):
    from app import Message
    test_message = "Test message from pytest"
    response = client.post("/message", data={"message": test_message}, follow_redirects=True)
    assert response.status_code == 200
    assert f"[{socket.gethostname()}] - {test_message}".encode() in response.data  # Match the message format
