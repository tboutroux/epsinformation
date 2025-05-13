import sys
import os
from datetime import datetime
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
    # Mock read_lines pour retourner différentes valeurs selon la table
    def mock_read_lines_side_effect(table, conditions=None):
        if table == "compte":
            return [{
                "email": "test@test.test",
                "password": "hashed",
                "username": "test.test",
                "role": 0,
                "id": 1,
            }]
        elif table == "post" and conditions and conditions.get("degre") == "3":
            return [{
                "id": 1,
                "titre": "Post important",
                "description": "Description du post",
                "degre": "3",
                "id_type": "1",
                "date": datetime.now()  # Ajout de la date
            }]
        elif table == "post" and conditions and conditions.get("id_type") == "4":
            return [{
                "id": 2,
                "titre": "Annonce emploi",
                "description": "Description de l'annonce",
                "id_type": "4",
                "date": datetime.now()  # Ajout de la date
            }]
        elif table == "post" and not conditions:
            return [{
                "id": 3,
                "titre": "Autre post",
                "description": "Contenu du post",
                "date": datetime.now()  # Ajout de la date
            }]
        elif table == "post_image":
            return [{
                "id_post": conditions.get("id_post", 1),
                "id_image": 1
            }]
        elif table == "image":
            return [{
                "id": 1,
                "contenu": b"fakeimage",
                "id_format": 1
            }]
        elif table == "format":
            return [{
                "id": 1,
                "libelle": "JPEG"
            }]
        return []

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