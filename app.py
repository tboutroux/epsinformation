from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
from db import *
from conf.configuration import conf

app = Flask(__name__)
app.secret_key = conf['secret_key']

@app.route("/")
def index():
    # Récupérer le nom d'utilisateur à partir de la session
    username = session.get('username')

    if username:
        return render_template('index.html', username=username)
    
    else:
        return render_template('index.html')

def hash_password(password):
    sha512 = hashlib.sha512()
    sha512.update(password.encode('utf-8'))
    hashed_password = sha512.hexdigest()
    return hashed_password

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        lastname = request.form['lastName']
        firstname = request.form['firstName']
        password = request.form['password']
        mail = request.form['mail']
        username = f"{firstname}.{lastname}"

        users = read_lines("compte", conditions={"nom": lastname, "prenom": firstname, "mail": mail})

        if lastname in users and hash_password(password) == users[username]['password']:
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
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        lastname = request.form['lastName']
        firstname = request.form['firstName']
        password = request.form['password']
        mail = request.form['mail']
        username = f"{firstname}.{lastname}"

        new_user = {
            'nom': lastname,
            'prenom': firstname,
            'mail': mail,
            'username': username,
            'password': hash_password(password)
        }

        users = read_lines("compte", conditions={"nom": lastname, "prenom": firstname, "mail": mail})

        if username in users:
            flash('Le nom d\'utilisateur est déjà pris. Veuillez choisir un autre.', 'danger')
        else:

            create_line("compte", new_user)
            flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)