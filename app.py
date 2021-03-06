from flask import Flask, request, render_template, url_for, redirect, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
from datetime import datetime
import json
from mcstatus import MinecraftServer
import rpyc
import os

# Custom
from helpers import login_required, login_user, create_user, get_servers, create_server, remove_server, get_users, remove_user, create_user_panel


# Set application
app = Flask(__name__)

# Set secret key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'for dev')

# Make templates auto-reload
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
@login_required
def index():

    return render_template("index.html", current_username = session.get("username"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    #session.clear()

    # If user logged in already, redirect to homepage
    if session.get("user_id") is not None:
        return redirect("/")

    # Check inputs here

    # User reached route via POST
    if request.method == "POST":

        if login_user(request.form.get("username"), request.form.get("password")):
            return redirect("/")
        else:
            # Show error on page
            return redirect("/login")

    # User reached route via GET
    else:
        return render_template("login.html")

@app.route("/servers")
def servers():

    user_servers = get_servers(session["user_id"])

    players = []

    try:
        conn = rpyc.connect("localhost", 42069)
        c = conn.root

        for server in user_servers:

            current_id = server[0]

            if not c.is_active(current_id):
                print(f"Server offline {current_id}")
                players.append("Offline")
            else:
                try:
                    server1 = MinecraftServer("127.0.0.1", server[4])
                    status1 = server1.status()
                    players.append(status1.players.online)
                except:
                    print("Couldn't reach server: ", server[2])
                    players.append("Unable to query")

    except:
        for server in user_servers:
            players.append("Offline")

    return render_template("servers.html", now=datetime.utcnow(), server_data=user_servers,
     current_username = session.get("username"), players=players)

# Server Actions
@app.route("/servers/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":

        # Check if inputs are empty
        # Server Name
        if request.form.get("name"):
            name = request.form.get("name")

        # Player Slots
        if request.form.get("slots"):
            slots = request.form.get("slots")

        # Port
        if request.form.get("port"):
            port = request.form.get("port")
        else:
            port = "25565"

        # Memory
        if request.form.get("memory"):
            memory = request.form.get("memory")
        else:
            memory = "1024"

        # JAR
        if request.form.get("jar"):
            jar = request.form.get("jar")

        if request.form.get("eula"):
            eula = request.form.get("eula")

        if create_server(name, memory, slots, port, jar, eula):
            # TODO: Create server via RPyC
            return redirect("/servers")
        else:
            # Return HTML error
            pass

    else:
        return render_template("create.html")


@app.route("/servers/remove", methods=["GET", "POST"])
@login_required
def remove():
    if request.method == "POST":

        server_id = request.form.get("server_id")

        remove_server(server_id)

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

    else:
        return redirect("/")

@app.route("/servers/start", methods=["GET", "POST"])
@login_required
def servers_start():
    if request.method == "POST":

        server_id = request.form.get("server_id")

        # user_id = session["user_id"]
        try:
            conn = rpyc.connect("localhost", 42069)
            c = conn.root

            print ("Attemping to start server " + server_id)

            if c.start_server(server_id):
                conn.close()
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
            else:
                conn.close()
                return json.dumps({'success':False}), 500, {'ContentType':'application/json'}
        except:
            print("Error while starting server")
            return json.dumps({'success':False}), 500, {'ContentType':'application/json'}
    else:
        return redirect("/")

@app.route("/servers/stop", methods=["GET", "POST"])
@login_required
def servers_stop():
    if request.method == "POST":

        server_id = request.form.get("server_id")

        # user_id = session["user_id"]

        try:

            conn = rpyc.connect("localhost", 42069)
            c = conn.root

            print ("Attemping to stop server " + server_id)

            if c.stop_server(server_id):
                conn.close()
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
            else:
                conn.close()
                return json.dumps({'success':False}), 500, {'ContentType':'application/json'}

            conn.close()
        except:
            print("Error while stopping server")
            return json.dumps({'success':False}), 500, {'ContentType':'application/json'}

    else:
        return redirect("/")

@app.route("/servers/restart", methods=["GET", "POST"])
@login_required
def servers_restart():
    if request.method == "POST":

        server_id = request.form.get("server_id")

        # user_id = session["user_id"]

        try:

            conn = rpyc.connect("localhost", 42069)
            c = conn.root

            print ("Attemping to restart server " + server_id)

            if c.restart_server(server_id):
                conn.close()
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
            else:
                conn.close()
                return json.dumps({'success':False}), 500, {'ContentType':'application/json'}

            conn.close()
        except:
            print("Error while restarting server")
            return json.dumps({'success':False}), 500, {'ContentType':'application/json'}

    else:
        return redirect("/")

@app.route("/servers/fetch", methods=["GET", "POST"])
@login_required
def servers_fetch():
    if request.method == "GET":

        user_servers = get_servers(session["user_id"])

        players = []

        try:
            conn = rpyc.connect("localhost", 42069)
            c = conn.root

            for server in user_servers:

                current_id = server[0]

                if not c.is_active(current_id):
                    print(f"Server offline {current_id}")
                    players.append("Offline")
                else:
                    try:
                        server1 = MinecraftServer("127.0.0.1", server[4])
                        status1 = server1.status()
                        players.append(status1.players.online)
                    except:
                        print("Couldn't reach server: ", server[2])
                        players.append("Unable to query")

        except:
            for server in user_servers:
                players.append("Offline")

        return render_template("servers_table.html", server_data=user_servers, players=players)

    else:
        return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":


        if create_user(request.form.get("username"), request.form.get("password"), request.form.get("email")):
            return redirect("/login")
        else:
            return redirect("/register")

    else:
        return render_template("register.html")

@app.route("/servers/<slug>")
@login_required
def selected(slug):

    # Select data from database using <slug> aka server_id
    return render_template("selected.html", server_id = slug)

@app.route("/users")
@login_required
def users():


    users = get_users()

    return render_template("users.html", current_username = session.get("username"), user_data=users)

@app.route("/users/fetch", methods=["GET", "POST"])
@login_required
def users_fetch():
    if request.method == "GET":

        users = get_users()

        return render_template("users_table.html", user_data=users)

    else:
        return redirect("/")

@app.route("/users/remove", methods=["GET", "POST"])
@login_required
def users_remove():

    if request.method == "POST":

        user_id = request.form.get("user_id")

        remove_user(user_id)

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

    else:
        return redirect("/")

@app.route("/users/create", methods=["GET", "POST"])
@login_required
def users_create():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        create_user_panel(username, password, email)

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

    else:
        return redirect("/")

@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")

@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect to homepage/login
    return redirect("/")