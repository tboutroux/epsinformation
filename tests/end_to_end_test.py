import pytest
from playwright.sync_api import sync_playwright


def run_with_assertion(page, assertion_func):
    try:
        assertion_func()
    except Exception as e:
        print("\n===== Playwright DEBUG: page content =====\n")
        print(page.content())
        page.screenshot(path="playwright_error.png")
        print("Screenshot saved as playwright_error.png")
        raise e


def test_register_and_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Remplace l'URL par celle de ton serveur Flask si besoin
        page.goto("http://localhost:5000/register")
        # Remplir le formulaire d'inscription
        page.fill('input[name="firstName"]', "TestPrenom")
        page.fill('input[name="lastName"]', "TestNom")
        page.fill('input[name="email"]', "testuser_e2e@example.com")
        page.fill('input[name="password"]', "testpassE2E")
        page.click('button[type="submit"]')
        # Vérifie la redirection vers la page de login
        page.wait_for_url("**/login")
        # Remplir le formulaire de connexion
        page.fill('input[name="email"]', "testuser_e2e@example.com")
        page.fill('input[name="password"]', "testpassE2E")
        page.click('button[type="submit"]')
        # Vérifie qu'on arrive sur la page d'accueil (index)
        page.wait_for_url("http://localhost:5000/")
        run_with_assertion(page, lambda: ("Bienvenue" in page.content() or "Epsinformation" in page.title()))
        browser.close()


def test_logout_and_redirect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Connexion préalable
        page.goto("http://localhost:5000/login")
        page.fill('input[name="email"]', "testuser_e2e@example.com")
        page.fill('input[name="password"]', "testpassE2E")
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:5000/")

        # Cliquer sur le dropdown de la navbar
        page.click('text=testprenom.testnom')

        # Attendre que le menu soit visible
        page.wait_for_selector('text=Déconnexion', timeout=1000)

        # Cliquer sur "Déconnexion"
        page.click('text=Déconnexion')
        
        # Vérifier la redirection vers la page d'accueil (login ou index selon logique)
        page.wait_for_url("**/login")
        run_with_assertion(page, lambda: ("Connexion" in page.content() or "Epsinformation" in page.title()))
        browser.close()


def test_edit_profile():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Connexion préalable
        page.goto("http://localhost:5000/login")
        page.fill('input[name="email"]', "testuser_e2e@example.com")
        page.fill('input[name="password"]', "testpassE2E")
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:5000/")

        # Cliquer sur le dropdown de la navbar
        page.click('text=testprenom.testnom')

        # Attendre que le menu soit visible
        page.wait_for_selector('text=Mon Compte', timeout=1000)

        # Cliquer sur "Mon Compte"
        page.click('text=Mon Compte')

        # Aller sur la page "Mon compte"
        page.wait_for_url("http://localhost:5000/account/testprenom.testnom")
        page.wait_for_selector('text=Modifier mon compte', timeout=1000)
        page.click('text=Modifier mon compte')

        page.wait_for_url("http://localhost:5000/edit_account/testprenom.testnom")

        # Modifier le prénom et le nom
        page.fill('input[name="firstname"]', "TestPrenomModif")
        page.fill('input[name="lastname"]', "TestNomModif")
        page.click('button[type="submit"]')

        # Vérifier la redirection et la présence du nouveau nom/prénom
        page.wait_for_url("http://localhost:5000/account/testprenommodif.testnommodif")
        run_with_assertion(page, lambda: "TestPrenomModif" in page.content())
        run_with_assertion(page, lambda: "TestNomModif" in page.content())
        browser.close()


def test_delete_account():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Connexion préalable
        page.goto("http://localhost:5000/login")
        page.fill('input[name="email"]', "testuser_e2e@example.com")
        page.fill('input[name="password"]', "testpassE2E")
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:5000/")

        # Cliquer sur le dropdown de la navbar avec le nouveau nom d'utilisateur
        page.click('text=testprenommodif.testnommodif')

        # Attendre que le menu soit visible
        page.wait_for_selector('text=Mon Compte', timeout=1000)

        # Cliquer sur "Mon Compte"
        page.click('text=Mon Compte')

        # Aller sur la page "Mon compte"
        page.wait_for_url("http://localhost:5000/account/testprenommodif.testnommodif")
        page.wait_for_selector('text=Supprimer mon compte', timeout=2000)

        # Cliquer sur "Supprimer mon compte"
        page.click('text=Supprimer mon compte')

        # Vérifier la redirection vers la page de login
        page.wait_for_url("**/login")
        run_with_assertion(page, lambda: ("Connexion" in page.content() or "Epsinformation" in page.title()))
        browser.close()


def test_create_post():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Connexion préalable
        page.goto("http://localhost:5000/login")
        page.fill('input[name="email"]', "test@test.test")
        page.fill('input[name="password"]', "test")
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:5000/")

        # Aller sur la page de création de post
        page.click('li.nav-item a.btn.btn-secondary')
        page.wait_for_url("http://localhost:5000/post")

        # Remplir le formulaire de création de post
        page.fill('input[name="title"]', "Titre E2E")
        page.fill('input[name="content"]', "Contenu du post E2E")
        page.select_option('select[name="type"]', value="4")
        page.select_option('select[name="degree"]', value="2")

        # Soumettre le formulaire
        page.click('button[type="submit"]')

        # Vérifier la redirection vers la page d'accueil et la présence du post
        page.wait_for_url("http://localhost:5000/")
        run_with_assertion(page, lambda: "Titre E2E" in page.content())
        run_with_assertion(page, lambda: "Contenu du post E2E" in page.content())
        browser.close()

def test_delete_post():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Connexion admin
        page.goto("http://localhost:5000/login")
        page.fill('input[name="email"]', "test@test.test")
        page.fill('input[name="password"]', "test")
        page.click('button[type="submit"]')
        page.wait_for_url("http://localhost:5000/")

        # Vérifier la présence du post
        run_with_assertion(page, lambda: "Titre E2E" in page.content())

        # Trouver la carte contenant le titre "Titre E2E" et cliquer sur son bouton de suppression
        card_headers = page.locator('.card-header')
        count = card_headers.count()
        found = False
        for i in range(count):
            header = card_headers.nth(i)
            if "Titre E2E" in header.inner_text():
                # Cliquer sur le bouton de suppression dans ce header
                delete_btn = header.locator('form[action^="/delete_post"] button[type="submit"]')
                delete_btn.click()
                found = True
                break
        assert found, "Le post à supprimer n'a pas été trouvé"

        # Attendre le rechargement et vérifier la disparition du post
        page.wait_for_url("http://localhost:5000/")
        run_with_assertion(page, lambda: "Titre E2E" not in page.content())
        browser.close()