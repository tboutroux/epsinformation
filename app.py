from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
from db import *
from conf.configuration import conf
import unidecode

app = Flask(__name__)
app.secret_key = conf['secret_key']

def hash_password(password):
    sha512 = hashlib.sha512()
    sha512.update(password.encode('utf-8'))
    hashed_password = sha512.hexdigest()
    return hashed_password

def format_username(column_name: str) -> str:
    """
    Formate le nom de la colonne en remplaçant les espaces par des underscores, 
    en mettant tout en minuscules,
    en supprimant les caractères spéciaux,
    et en remplaçant les caractères accentués par leur équivalent non accentué.

    Args:
        column_name (str): Nom de la colonne à formater

    Returns:
        str: Nom de la colonne formaté
    """
    # Convertir en minuscules
    column_name = column_name.lower()
    
    # Remplacer les espaces par des underscores
    column_name = column_name.replace(" ", "_")

    # Remplacer les apostrophes par des underscores
    column_name = column_name.replace("'", "_")

    # Remplacer les - par des underscores
    column_name = column_name.replace("-", "_")
    
    # Remplacer les caractères accentués par leur équivalent non accentué
    column_name = unidecode.unidecode(column_name)

    return column_name

@app.route("/")
def index():
    # Récupérer le nom d'utilisateur à partir de la session
    username = session.get('username')

    if username:
        return render_template('index.html', username=username)
    
    else:
        return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:

            password = request.form['password']
            mail = request.form['email']

            users = read_lines("compte", conditions={"email": mail})

            if mail == users[0]['email'] and hash_password(password) == users[0]['password']:
                session['username'] = users[0]['username']
                return redirect(url_for('index'))
            else:
                print('Échec de la connexion. Vérifiez votre nom d\'utilisateur et votre mot de passe.', 'danger')

        except Exception as e:
            print(f"Error: {e}")
            flash('Une erreur s\'est produite lors de la connexion. Veuillez réessayer.', 'danger')

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
    message = ''
    if request.method == 'POST':

        try:
            lastname = request.form['lastName']
            firstname = request.form['firstName']
            password = request.form['password']
            mail = request.form['email']
            username = format_username(firstname) + "." + format_username(lastname)
            role = "1" if mail in conf['admins'] else "0"

            print(username)

            new_user = {
                'nom': lastname,
                'prenom': firstname,
                'email': mail,
                'username': username,
                'password': hash_password(password),
                'role': role
            }

            users = read_lines("compte", conditions={"nom": lastname, "prenom": firstname, "email": mail})

            if username in users:
                message = 'Le nom d\'utilisateur est déjà utilisé.'

            elif mail in users :
                message = 'L\'adresse e-mail est déjà utilisée ou n\'est pas autorisée.'
            else:

                create_line("compte", new_user)
                message = 'Inscription réussie! Vous pouvez maintenant vous connecter.'
                return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Error: {e}")
            flash('Une erreur s\'est produite lors de l\'inscription. Veuillez réessayer.', 'danger')

    if message:
        return render_template('register.html', message=message)
    
    else:
        return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)