from functools import wraps
from flask import redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
from webapp.models import User, Server, Jar
from webapp.extensions import db
import os

def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def login_user(username, password):

    # Check username in database
    try:

        user = User.query.filter_by(username=username).first()

        if not user:
            return False

        if not check_password_hash(user.password, password):
            return False

        session["user_id"] = user.id
        session["username"] = username

    except (Exception) as error :
        print ("Error while logging user in", error)
        return False
    finally:
        return True


def get_servers(userid):

    # Get servers from database
    try:
        servers = Server.query.all()
        print("Selected servers from database")

    except (Exception) as error :
        print ("Error while selecting servers from database", error)
        return False
    finally:
        return servers


def create_server(name, memory, slots, port, jar):
    # Insert server into database

    server_id = None

    try:

        new_server = Server(name=name, memory=memory, slots=slots, port=port, jar=jar)
        db.session.add(new_server)
        db.session.commit()

        server_id = new_server.id

        print("Inserted server into database")

    except (Exception) as error :
        print ("Error while creating server in database", error)
        return False
    finally:
        return server_id


def remove_server(server_id):
    # Remove server from database
    try:

        server = Server.query.get_or_404(server_id)
        db.session.delete(server)
        db.session.commit()

        print("Removed server from database")

    except (Exception) as error :
        print ("Error while removing server from database", error)
        return False
    finally:

            return True


def get_users():

    # Get users from database
    try:

        users = User.query.all()

        print("Selected users from database")

    except (Exception) as error :
        print ("Error while selecting users from database", error)
        return False
    finally:
                
            return users


def remove_user(user_id):
    # Remove user from database
    try:

        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        print("Removed user from database")

    except (Exception) as error :
        print ("Error while removing user from database", error)
        return False
    finally:

            return True

def create_user_panel(username, password, email):
    # Insert user into database
    try:


        new_user = User(email=email, username=username, passhash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        print("Created TP user in database")

    except (Exception) as error :
        print ("Error while creating TP user in database", error)
        return False
    finally:

            return True



def create_user(username, password, email):
    # Insert user into database
    try:

        new_user = User(email=email, username=username, passhash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id
        session["username"] = username

    except (Exception) as error :
        print ("Error while creating user in database", error)
        return False
    finally:
            return True

def save_jar(jarFile, jarName):

    filename = jarFile.filename
    ext = filename.rsplit(".", 1)[1]

    if filename == "":
        print("JarFile has no name, redirecting")
        return False

    if not "." in filename:
        print("No file extension")
        return False
    
    if ext.upper() != "JAR":
        print("Not a jar file")
        return False

    try:
        # Insert jar into database
        new_jar = Jar(name=jarName, file=filename)
        db.session.add(new_jar)
        db.session.commit()

        # Save jar file locally
        jarDirectory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../jars/")
        jarFile.save(os.path.join(jarDirectory, jarFile.filename))

    except (Exception) as error :
        print ("Error while saving/inserting jar", error)
        return False
    finally:
            return True