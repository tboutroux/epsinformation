import time
from unittest.mock import patch, MagicMock
from app import hash_password, format_username, get_weather_of_the_day
from db import create_line, read_lines, delete_line, get_db_connection, update_line, line_exists

# ---------- TESTS UNITAIRES ----------

def test_hash_password_consistency():
    pw = "test123"
    assert hash_password(pw) == hash_password(pw)

def test_hash_password_difference():
    assert hash_password("abc") != hash_password("def")

def test_format_username_simple():
    assert format_username("Jean-Pierre") == "jean_pierre"

def test_format_username_accent():
    assert format_username("Élise Dubois") == "elise_dubois"

def test_format_username_apostrophe():
    assert format_username("O'Neil") == "o_neil"


