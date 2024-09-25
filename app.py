from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
from db import *
from conf.configuration import conf
import unidecode
import requests
from PIL import Image
from io import BytesIO
import base64

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

def get_weather_of_the_day():
    """
    Récupère les prévisions météorologiques pour la journée actuelle à partir de l'API MeteoConcept.

    Returns:
        dict: Dictionnaire contenant les prévisions météorologiques pour la journée actuelle.
    """
    response = { 'code': 400, 'error': '', 'data': [] }

    try:
        req = requests.get(f"{conf['weather_api']['base_url']}?token={conf['weather_api']['api_key']}&insee={conf['weather_api']['insee']}")

        if req.status_code == 200:
            response['code'] = 200
            response['data'] = req.json()['forecast'][0]

        else:
            response['error'] = 'Erreur lors de la récupération des données météorologiques.'

    except Exception as e:
        response['error'] = f"Erreur lors de la récupération des données météorologiques: {e}"

    return response

# Ajouter un filtre b64encode
@app.template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

@app.route("/")
def index():
    # Récupérer le nom d'utilisateur à partir de la session
    username = session.get('username')

    weather = get_weather_of_the_day()['data']

    # On récupère le code météo, le nom de la ville et la température
    weather = {
        'weather': weather['weather'],
        'tmin': weather['tmin'],
        'tmax': weather['tmax']
    }

    # On récupère le dernier post ayant un degré de 1
    most_important_post = read_lines("post", conditions={"degre": "3"})

    if most_important_post:
        most_important_post = most_important_post[-1]

        # On récupère l'image associée au post
        image = read_lines("post_image", conditions={"id_post": most_important_post['id']})

        if image:
            image = read_lines("image", conditions={"id": image[0]['id_image']})[0]

            # On convertit les données
            image_data = image['contenu']
            image_format = read_lines("format", conditions={"id": image['id_format']})[0]['libelle']

            # On crée un objet Image à partir des données binaires
            image = Image.open(BytesIO(image_data))

            # On sauvegarde les données de l'image dans des variables
            image_width, image_height = image.size
            image_format = image.format

            # On crée un dictionnaire contenant les données de l'image
            image = {
                'data': image_data,
                'width': image_width,
                'height': image_height,
                'format': image_format
            }

        most_important_post['image'] = image

        print(most_important_post)

    if username:
        return render_template('index.html', username=username, weather=weather, most_important_post=most_important_post)
    
    else:
        return render_template('index.html', weather=weather)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:

            password = request.form['password']
            mail = request.form['email']

            users = read_lines("compte", conditions={"email": mail})

            if mail == users[0]['email'] and hash_password(password) == users[0]['password']:
                session['username'] = users[0]['username']
                session['role'] = users[0]['role']
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

@app.route('/post', methods=['GET', 'POST'])
def post():

    if not session.get('username'):
        print('Vous devez être connecté pour créer un post.')
        message = 'Vous devez être connecté pour créer un post.'
        return redirect(url_for('login', message=message))

    if request.method == 'POST':
        try:
            title = request.form['title']
            content = request.form['content']
            post_type = request.form['type']
            degree = request.form['degree']
            username = session.get('username')

            if not session.get('username'):
                flash('Vous devez être connecté pour créer un post.', 'warning')
                return redirect(url_for('login'))

            # Gestion de l'image
            if 'image' not in request.files:
                flash('Aucune image sélectionnée.', 'warning')
                return redirect(request.url)
            
            file = request.files['image']

            if file.filename == '':
                flash('Aucune image sélectionnée.', 'warning')
                return redirect(request.url)
            
            if file:
                # Lire les données de l'image
                image_data = file.read()

                # On convertit les données de l'image en blob
                image_data = BytesIO(image_data).read()   
                
                # Utilisation de Pillow pour récupérer le format de l'image
                image = Image.open(BytesIO(image_data))
                image_format = image.format  # Par exemple, JPEG, PNG

                new_format = {
                    'libelle': image_format
                }

                # Vérifier si le format de l'image existe déjà dans la base de données
                formats = read_lines("format", conditions={"libelle": image_format})

                if not formats:
                    # Insertion du format dans la table "format"
                    create_line("format", new_format)

                # On récupère l'ID du format inséré
                image_format = read_lines("format", conditions={"libelle": image_format})[0]['id']

                # Préparer les données de l'image pour la base de données
                new_image = {
                    'contenu': image_data,  # Les données binaires de l'image
                    'id_format': image_format  # Le format de l'image
                }

                # Insertion de l'image dans la table "image"
                create_line("image", new_image)

                # Récupérer l'ID de l'image insérée
                image_id = read_lines("image")[-1]['id']

                user_id = read_lines("compte", conditions={"username": username})[0]['id']

                # Préparer les données du post
                new_post = {
                    'titre': title,
                    'description': content,
                    'id_type': post_type,
                    'degre': degree,
                    'id_compte': user_id,
                }

                # Insertion du post dans la table "posts"
                create_line("post", new_post)

                # On récupère l'ID du post inséré
                post_id = read_lines("post")[-1]['id']

                # Préparer les données de la relation entre le post et l'image
                new_post_image = {
                    'id_post': post_id,
                    'id_image': image_id
                }

                # Insertion de la relation dans la table "post_image"
                create_line("post_image", new_post_image)

                flash('Post créé avec succès!', 'success')
                return redirect(url_for('index'))

        except Exception as e:
            print(f"Error: {e}")
            flash('Une erreur s\'est produite lors de la création du post. Veuillez réessayer.', 'danger')

    username = session.get('username')
    return render_template('post.html', username=username)

if __name__ == "__main__":
    app.run(debug=True)