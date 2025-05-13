import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock
from app import app, get_weather_of_the_day

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_login_route_success(client):
    # Mock read_lines pour retourner un utilisateur valide
    with patch("app.read_lines") as mock_read_lines, patch("app.hash_password") as mock_hash_password:
        mock_read_lines.return_value = [{
            "email": "testuser@example.com",
            "password": "hashed",
            "username": "testuser",
            "role": 0,
            "id": 1,
        }]
        mock_hash_password.return_value = "hashed"
        response = client.post("/login", data={
            "email": "test@test.test",
            "password": "test"
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Annonces" in response.data

def test_login_route_failure(client):
    with patch("app.read_lines") as mock_read_lines:
        mock_read_lines.return_value = []
        response = client.post("/login", data={
            "email": "wrong@example.com",
            "password": "wrongpass"
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"connexion" in response.data.lower() or b"login" in response.data.lower()

@patch("app.requests.get")
def test_get_weather_of_the_day_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"forecast": [{"weather": 1, "tmin": 10, "tmax": 20}]}
    mock_get.return_value = mock_response

    result = get_weather_of_the_day()
    assert result["code"] == 200
    assert result["data"]["weather"] == 1
    assert result["data"]["tmin"] == 10
    assert result["data"]["tmax"] == 20

@patch("app.requests.get")
def test_get_weather_of_the_day_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    result = get_weather_of_the_day()
    assert result["code"] == 400
    assert "erreur" in result["error"].lower() or result["error"] != ""