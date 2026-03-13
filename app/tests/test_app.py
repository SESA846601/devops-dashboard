import sys
import os

# DevOps Dashboard - Pipeline Test
# Checking with ngrok


# Allow import from parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app


def test_dashboard_returns_200():
    """Dashboard route should respond successfully."""
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200


def test_dashboard_contains_title():
    """Dashboard HTML should contain the app title."""
    client = app.test_client()
    response = client.get('/')
    assert b'DevOps Dashboard' in response.data


def test_api_info_returns_json():
    """/api/info should return valid JSON with a status field."""
    client = app.test_client()
    response = client.get('/api/info')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'running'