from flask import Flask, render_template, request
import logger
import sqlite3

n,na,nu, p = "","","", ""

# Création de l'Application Flask
app = Flask(__name__)

conn = sqlite3.connect('rep.db', check_same_thread=False)
cur = conn.cursor()

# Commande qui vérifie la validité des entrées dans les 
def check_auth(n,na,nu):
    # Vérifie si l'utilisateur n'est pas détecté 
    if not n:
        return "Erreur d'Authentification. Veuillez vous reconnecter."
    # Vérifie si le numéro ET le nom ne sont pas renseignés
    elif not nu and not na:
        return "Immpossible d'attribuer un numéro vide à un contact vide dans votre répertoire."
    # Vérifie si le nom est absent
    elif not na:
        return "Immpossible d'ajouter un contact vide à votre répertoire."
    # Vérifie si le numéro est absent
    elif not nu:
        return "Immpossible d'ajouter un numéro vide à votre répertoire."
    # Vérifie si le numéro est valide : s'il y a 10 entrées, ou 14 (en comptant les points XX.XX.XX.XX.XX)
    elif len(nu) not in ([10,14]):
        return "Impossible d'ajouter un numéro invalide à votre répertoire."
    else:
        return False

# Commande qui ajoute les entrées à la base de donnée. Permet de prendre en compte la création d'une table selon le nom d'utilisateur.
def add_bdd(username, name, number):
    conn = sqlite3.connect('rep.db', check_same_thread=False)
    cur = conn.cursor()
    # Créer une table si aucune n'existe
    cmd = "CREATE TABLE IF NOT EXISTS {} (name_c TEXT, number TEXT)".format(username)
    cur.execute(cmd)

    # Vérifie si le nom de contact existe 
    cmd = f"SELECT name_c FROM '{username}' WHERE name_c LIKE ?"
    cur.execute(cmd, (name + '%',))
    rows = cur.fetchall()
    
    # Si le nom existe déjà, le nom sera légèrement changé, avec une numérotation
    if len(rows) > 0:
        num = len(rows) + 1
        name = f"{name}_{num}"
        
    # Permet d'ajouter la valeur dans la table dédiée à l'utilisateur
    cmd = "INSERT INTO {} VALUES (?, ?)".format(username)
    cur.execute(cmd, (name, number))

    conn.commit()
    cur.close()
    conn.close()

# Commande de recherche dans la base de donnée
def search_bdd(username, name):
    conn = sqlite3.connect('rep.db', check_same_thread=False)
    cur = conn.cursor()
    # Créer une table si aucune table n'existe au nom de l'utilisateur
    cmd = f"CREATE TABLE IF NOT EXISTS {username} (name_c TEXT, number TEXT)"
    cur.execute(cmd)
    # Cherche les numéros attribués au nom, en cherchant même si plusieurs existent.
    cmd = "SELECT number FROM {} WHERE name_c LIKE ?".format(username)
    cur.execute(cmd, (name+'%',))
    result = cur.fetchall()
    # Fermeture de la bdd par sécurité.
    cur.close()
    conn.close()
    # S'il y a des résultats, mettre en forme leur renvoie via return
    if result:
        if len(result) > 1:
            result2 = ""
            cpt = 1
            for row in result:
                result2 += f"{name}_{cpt} : {row[0]}. | "
                cpt += 1
            return result2
        else:
            return f"{name} : {result[0][0]}. "
    else:
        return "Aucune entrée trouvée à ce nom"

# Permet de lister le contenu de la table au nom de l'utilisateur
def list_bdd(username):
    conn = sqlite3.connect('rep.db', check_same_thread=False)
    cur = conn.cursor()
    # Créer une table si aucune table n'existe au nom de l'utilisateur
    cmd = f"CREATE TABLE IF NOT EXISTS {username} (name_c TEXT, number TEXT)"
    cur.execute(cmd)
    # Créer la liste de contacts dans la table
    cmd = "SELECT * FROM {}".format(username)
    cur.execute(cmd)
    result = cur.fetchall()
    # Fermeture de la bdd par sécurité.
    cur.close()
    conn.close()
    # S'il y a des résultats, mettre en forme leur renvoie via return
    if result:
        if len(result) > 1:
            result2 = ""
            cpt = 1
            for row in result:
                result2 += f"{row[0]} : {row[1]}. | "
            return result2
        else:
            return f"{result[0][0]} : {result[0][1]}. "
    else:
        return "Pas de contact enregistré sur votre compte."

# Page d'accueil, permettant de choisir si l'on préfère se connecter ou créer un compte
@app.route('/', methods = ['Post','GET'])
def index():
    return render_template("index.html")

# Page de connexion
@app.route('/login', methods = ['Post'])
def login():
    return render_template("login.html")

# Page de création de compte
@app.route('/signup', methods = ['Post'])
def signup():
    return render_template("signup.html")

# Page d'accueil depuis laquelle on sélectionne si l'on préfère lister la base de donnée, chercher un contact, ou en ajouter un.
@app.route('/main', methods = ['Post'])
def main():
    result = request.form
    print(result)
    global n, p
    if 'Login' in result or 'Signup' in result :
        n = result['username']
        p = result['password']
    else:
        n, p = n, p
    # Vérifie si l'utilisateur s'est connecté à un compte déjà existant
    if 'Login' in result:
        if logger.login(n,p):
            return render_template("main.html",username=n,password=p)
        else:
            if n == "":
                error_n = "Impossible de se Connecter. Veuillez renseigner un nom d'utilisateur."
            elif p == "":
                error_n = "Impossible de se Connecter. Veuillez renseigner un mot de passe."
            else:
                error_n = "Impossible de se Connecter. Mot de passe ou nom d'utilisateur invalides."
            return render_template("login.html",error_n=error_n)
    # Vérifie si l'utilisateur a crée un compte
    if 'Signup' in result:
        if logger.signup(n,p):
            return render_template("main.html",username=n,password=p)
        else:
            if n == "":
                error_n = "Impossible de Créer un Compte. Veuillez renseigner un nom d'utilisateur."
            elif p == "":
                error_n = "Impossible de Créer un Compte. Veuillez renseigner un mot de passe."
            elif len(p) < 8 or not any(char.isdigit() for char in p) or not any(char.isalpha() for char in p) or p.isalnum():
                error_n = "Impossible de Créer un Compte. Le mot de passe doit contenir au moins 8 caractères dont au moins 1 caractère spécial."
            elif logger.check_user(n):
                error_n = "Impossible de Créer un Compte. Le nom d'utilisateur existe déjà."
            elif " " in n:
                error_n = "Impossible de Créer un Compte. Le nom d'utilisateur contient un espace."
            else:
                error_n = "Impossible de Créer un Compte. Erreur inconnue. "
            return render_template("signup.html",error_n=error_n)
    # Vérifie si l'utilisateur a utilisé l'option pour retourner au menu principal
    if 'Menu' in result:
        if logger.login(n,p):
            return render_template("main.html",username=n,password=p)
        else:
            error_n = "Impossible d'Accéder à la Page. Veuillez vous connecter."
            return render_template("error.html",error_n=error_n)
    # Vérifie si l'utilisateur a utilisé l'option pour se déconnecter
    if 'Logout' in result:
        return render_template("index.html")
    else:
        error_n = "Impossible d'Accéder à la Page. Veuillez vous connecter."
        return render_template("error.html",error_n=error_n)

# Page de listing de contacts
@app.route('/rep_list', methods = ['Post','GET'])
def rep_list():
    if not logger.login(n,p):
        error_n = "Impossible d'Accéder à la Page. Veuillez vous connecter."
        return render_template("error.html",error_n=error_n)
    return render_template("rep_list.html",username=n,password=p)

# Page de recherche de contact
@app.route('/rep_index', methods = ['Post','GET'])
def rep_index():
    if not logger.login(n,p):
        error_n = "Impossible d'Accéder à la Page. Veuillez vous connecter."
        return render_template("error.html",error_n=error_n)
    return render_template("rep_index.html",username=n,password=p)

# Page d'ajout de contact
@app.route('/rep_add', methods = ['Post','GET'])
def rep_add():
    if not logger.login(n,p):
        error_n = "Impossible d'Accéder à la Page. Veuillez vous connecter."
        return render_template("error.html",error_n=error_n)
    return render_template("rep_add.html",username=n,password=p)

# Page de résultat permettant d'afficher les résultats renvoyés par les commandes.
@app.route('/results', methods = ['Post','GET'])
def results():
    if not logger.login(n,p):
        error_n = "Impossible d'Accéder à la Page. Veuillez vous connecter."
        return render_template("error.html",error_n=error_n)
    result = request.form
    # Vérifie si le résultat est un ajout de contact
    if 'Add' in result:
        na = result['name_ca']
        nu = result['number']
        if not check_auth(n,na,nu):
            if len(nu) == 10:
                n2 = '.'.join([nu[i:i+2] for i in range(0, len(nu), 2)])
                add_bdd(n,na,n2)
                res = f'{n2} a bien été enregistré au nom de {na}'
            elif len(nu) == 14:
                add_bdd(n,na,nu)
                res = f'{nu} a bien été enregistré au nom de {na}'
        else:
            res = check_auth(n,na,nu) 
        return render_template("rep_add.html",res=res,username=n)
    # Vérifie si le résultat est une recherche de contact
    if 'Index' in result:
        na = result['name_ci']
        if na :
            res = search_bdd(n,na)
        elif not na:
            res = "Immpossible de chercher un nom vide dans votre répertoire."
        return render_template("rep_index.html",res=res,username=n)
    # Vérifie si le résultat est la liste des contacts
    if 'Lister' in result:
        res = list_bdd(n)
        return render_template("rep_list.html",res=res,username=n)
    else:
        return render_template("error.html",error_n="Impossible d'Accéder à la Page. Veuillez vous connecter.")
    

app.run(debug = True)
