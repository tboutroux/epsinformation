import time
from app import hash_password
from db import create_line, read_lines, delete_line

# ---------- TESTS DE PERFORMANCE ----------

def test_read_lines_performance():
    start = time.time()
    users = read_lines("compte")
    duration = time.time() - start
    assert duration < 1  # Doit répondre en moins d'1 seconde

def test_create_and_delete_line_performance():
    test_user = {
        "nom": "PerfNom",
        "prenom": "PerfPrenom",
        "email": "perfuser@example.com",
        "username": "perfuser",
        "password": hash_password("perfpass"),
        "role": 0
    }
    start = time.time()
    create_line("compte", test_user)
    delete_line("compte", {"username": "perfuser"})
    duration = time.time() - start
    assert duration < 1  # Doit répondre en moins d'1 seconde