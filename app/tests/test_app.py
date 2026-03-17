import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app


def test_dashboard_returns_200():
    client = app.test_client()
    assert client.get('/').status_code == 200


def test_dashboard_contains_title():
    client = app.test_client()
    assert b'DevOps Dashboard' in client.get('/').data


def test_health_endpoint():
    client = app.test_client()
    res = client.get('/health')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'ok'


def test_api_info_returns_json():
    client = app.test_client()
    res = client.get('/api/info')
    assert res.status_code == 200
    assert 'status' in res.get_json()