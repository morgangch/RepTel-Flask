import hashlib, json, os, secrets, re
from flask import Flask

def hash_password(password):
    #Hache un mot de passe en utilisant SHA-256
    hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hash

def hash_username(username):
    #Hache un nom d'utilisateur en utilisant SHA-512
    hash = hashlib.sha512(username.encode('utf-8')).hexdigest()
    return hash

# Vérifie si le mot de passe correspond au mot de passe enregistré au nom d'utilisateur enregistré
def check_password(username, password):
    # Charge le json des mots de passe s'il contient quelque chose : autrement renvoie False.
    if os.path.exists('users2.json') and os.path.getsize('users2.json') > 0:
        with open('users2.json', 'r') as f:
            users = json.load(f)
            f.close()
    else:
        return False
    hashed_username = hash_username(username)
    # Vérifie si le nom d'utilisateur existe dans le json
    if hashed_username not in users:
        return False
    hash = users[hashed_username]['password']
    # Vérifie si l'utilisateur peut se connecter : si son mot 
    return hash == hash_password(password)
    
#Vérifie si l'utilisateur est présent dans la base de données
def check_user(username):
    # Charge le json des mots de passe s'il contient quelque chose : autrement renvoie False.
    if os.path.exists('users2.json') and os.path.getsize('users2.json') > 0:
        with open('users2.json', 'r') as f:
            users = json.load(f)
            f.close()
    else:
        return False
    hashed_username = hash_username(username)
    return hashed_username in users

# Code de création de compte
def signup(username, password):
    # Si le nom d'utilisateur contient un espace, empêcher la création du compte
    if " " in username:
        return False
    
    # Charge le json des comptes s'il contient quelque chose : autrement créer un nouveau dictionnaire vide
    if os.path.exists('users2.json') and os.path.getsize('users2.json') > 0:
        with open('users2.json', 'r') as f:
            users = json.load(f)
            f.close()
    else:
        users = {}

    # Vérifie s'il est possible de se connecter avec ce meme nom d'utilisateur : si c'est le cas, le nom est déjà utilisé.
    if check_user(username):
        print("Impossible : Le nom d'utilisateur existe déjà.")
        return False
    
    # Vérifie si le mot de passe respecte les règles
    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password) or password.isalnum():
        print("Impossible : Le mot de passe doit contenir au moins 8 caractères dont au moins 1 caractère spécial.")
        return False
    
    hashed_password = hash_password(password)

    hashed_username = hash_username(username)
    
    # Crée le compte
    users[hashed_username] = {'password': hashed_password}
    with open('users2.json', 'w') as f:
        json.dump(users, f)
        f.close()
    return True

# Code de connexion à un compte
def login(username, password):
    # Charge le json des mots de passe s'il contient quelque chose : autrement renvoie False.
    if os.path.exists('users2.json') and os.path.getsize('users2.json') > 0:
        with open('users2.json', 'r') as f:
            users = json.load(f)
            f.close()
    else:
        return False
    hashed_username = hash_username(username)
    if not users or hashed_username not in users:
        return False
    hash = users[hashed_username]['password']
    # Vérifie si le mot de passe concorde
    return hash == hash_password(password)