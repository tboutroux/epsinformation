from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
from db import *

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

def hash_password(password):
    sha512 = hashlib.sha512()
    sha512.update(password.encode('utf-8'))
    hashed_password = sha512.hexdigest()
    return hashed_password

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = read_lines("compte")

        if username in users and hash_password(password) == users[username]['password']:
            flash('Connexion réussie!', 'success')
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Échec de la connexion. Vérifiez votre nom d\'utilisateur et votre mot de passe.', 'danger')

    return render_template('login.html')

@app.route('/account')
def dashboard():
    # Récupérer le nom d'utilisateur à partir de la session
    username = session.get('username')
    
    if username:
        return render_template('dashboard.html', username=username)
    else:
        flash('Vous devez vous connecter pour accéder au tableau de bord.', 'warning')
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    # Supprimer le nom d'utilisateur de la session (déconnexion)
    session.pop('username', None)
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = read_lines("compte")

        # Vérifier si le nom d'utilisateur est déjà utilisé
        if username in users:
            flash('Le nom d\'utilisateur est déjà pris. Veuillez choisir un autre.', 'danger')
        else:
            # Ajouter l'utilisateur à la base de données (ici, stockage en mémoire pour la démonstration)
            users[username] = {'username': username, 'password': hash_password(password)}
            flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)