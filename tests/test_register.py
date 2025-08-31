import os
import tempfile
import json
from wsgiref import headers

import pytest
import sys
import os

# ensure project root is on sys.path so `import app` works when pytest runs
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app as flask_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_file = tmp_path / 'test_uman.db'
    monkeypatch.setenv('UMAN_DB_PATH', str(db_file))
    monkeypatch.setenv('TESTING_RETURN_CODE', '1')
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


def test_register_and_confirm_flow(client):
    # Register
    resp = client.post('/register', data={
        'prenom': 'Jean',
        'nom': 'Dupont',
        'email': 'jean@example.com',
        'organisation': 'TestOrg',
        'telephone': '1234567890'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['email'] == 'jean@example.com'
    code = data['code']
    assert code

    # Confirm with wrong code
    resp2 = client.post('/register/confirm', data={'email': 'jean@example.com', 'code': 'wrongcode'})
    assert resp2.status_code == 400

    # Confirm with correct code
    resp3 = client.post('/register/confirm', data={'email': 'jean@example.com', 'code': code})
    assert resp3.status_code == 200
    res3 = resp3.get_json()
    assert res3['ok'] is True
