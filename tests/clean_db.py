# Script de nettoyage de la base de données pour les tests E2E
from db import delete_line

def clean_test_data():
    # Supprime les utilisateurs de test
    delete_line("compte", {"email": "testuser_e2e@example.com"})
    delete_line("compte", {"email": "test@test.test"})
    # Supprime les posts de test
    delete_line("post", {"titre": "Titre E2E"})
    # Ajoute ici d'autres suppressions si besoin

if __name__ == "__main__":
    clean_test_data()
    print("Nettoyage terminé.")
