from flask import Blueprint, render_template, session, redirect, request
from webapp.helpers import login_required, login_user, get_servers, create_server, remove_server, get_users, create_user_panel, create_user, remove_user, save_jar, get_jars
from mcstatus import MinecraftServer
import rpyc
from datetime import datetime
import json

main = Blueprint("main", __name__)

@main.route("/")
@login_required
def index():
    return render_template("index.html", current_username = session.get("username"))


@main.route("/login", methods=["GET", "POST"])
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


@main.route("/servers")
def servers():

    user_servers = get_servers(session["user_id"])
    jars = get_jars()

    players = []

    try:
        conn = rpyc.connect("localhost", 42069)
        c = conn.root

        for server in user_servers:

            current_id = server.id

            if not c.is_active(current_id):
                print(f"Server offline {current_id}")
                players.append("Offline")
            else:
                try:
                    server1 = MinecraftServer("127.0.0.1", server.port)
                    status1 = server1.status()
                    players.append(status1.players.online)
                except Exception as e:
                    print(e)
                    print("Couldn't reach server: ", server.name)
                    players.append("Unable to query")

    except Exception as e:
        print(e)
        for server in user_servers:
            players.append("Offline")

    return render_template("servers.html", now=datetime.utcnow(), server_data=user_servers,
     current_username = session.get("username"), players=players, jar_data=jars)


@main.route("/servers/create", methods=["GET", "POST"])
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


        server_id = create_server(name, memory, slots, port, jar)

        if server_id is not None:

            server_id = str(server_id)
            print(f"The server id is {server_id}")

            try:
                conn = rpyc.connect("localhost", 42069)
                c = conn.root

                if c.create_server(server_id, port):
                    conn.close()
                    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
                else:
                    conn.close()
                    return json.dumps({'success':False}), 500, {'ContentType':'application/json'}
            except Exception as e:
                print(e)
                print("Error while creating server")
                return json.dumps({'success':False}), 500, {'ContentType':'application/json'}


            return redirect("/servers")
        else:
            # Return HTML error
            pass

    else:
        return render_template("create.html")


@main.route("/servers/remove", methods=["GET", "POST"])
@login_required
def remove():
    if request.method == "POST":

        server_id = str(request.form.get("server_id"))

        try:
            remove_server(server_id)

            conn = rpyc.connect("localhost", 42069)
            c = conn.root

            if c.remove_server(server_id):
                conn.close()
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
            else:
                conn.close()
                return json.dumps({'success':False}), 500, {'ContentType':'application/json'}
        except Exception as e:
            print(e)
            print("Error while removing server")
            return json.dumps({'success':False}), 500, {'ContentType':'application/json'}

    else:
        return redirect("/")


@main.route("/servers/start", methods=["GET", "POST"])
@login_required
def servers_start():

    if request.method == "POST":

        server_id = str(request.form.get("server_id"))

        try:
            conn = rpyc.connect("localhost", 42069)
            c = conn.root

            print ("Attemping to start server " + server_id)

            if c.start_server(server_id):
                print("Server Started Successfully")
                conn.close()
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
            else:
                print("Server didn't start")
                conn.close()
                return json.dumps({'success':False}), 500, {'ContentType':'application/json'}
        except Exception as e:
            print(e)
            print("Error while starting server")
            return json.dumps({'success':False}), 500, {'ContentType':'application/json'}
    else:
        return redirect("/")

@main.route("/servers/stop", methods=["GET", "POST"])
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

@main.route("/servers/restart", methods=["GET", "POST"])
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

@main.route("/servers/fetch", methods=["GET", "POST"])
@login_required
def servers_fetch():
    if request.method == "GET":

        user_servers = get_servers(session["user_id"])

        players = []

        try:
            conn = rpyc.connect("localhost", 42069)
            c = conn.root

            for server in user_servers:

                current_id = server.id

                if not c.is_active(current_id):
                    print(f"Server offline {current_id}")
                    players.append("Offline")
                else:
                    try:
                        server1 = MinecraftServer("127.0.0.1", server.port)
                        status1 = server1.status()
                        players.append(status1.players.online)
                    except Exception as e:
                        print(e)
                        print("Couldn't reach server: ", server.name)
                        players.append("Unable to query")

        except:
            for server in user_servers:
                players.append("Offline")

        return render_template("servers_table.html", server_data=user_servers, players=players)

    else:
        return redirect("/")

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":


        if create_user(request.form.get("username"), request.form.get("password"), request.form.get("email")):
            return redirect("/login")
        else:
            return redirect("/register")

    else:
        return render_template("register.html")

@main.route("/servers/<slug>")
@login_required
def selected(slug):

    # Select data from database using <slug> aka server_id
    return render_template("selected.html", server_id=slug, current_username = session.get("username"))

@main.route("/users")
@login_required
def users():


    users = get_users()

    return render_template("users.html", current_username = session.get("username"), user_data=users)

@main.route("/users/fetch", methods=["GET", "POST"])
@login_required
def users_fetch():
    if request.method == "GET":

        users = get_users()

        return render_template("users_table.html", user_data=users)

    else:
        return redirect("/")

@main.route("/users/remove", methods=["GET", "POST"])
@login_required
def users_remove():

    if request.method == "POST":

        user_id = request.form.get("user_id")

        remove_user(user_id)

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

    else:
        return redirect("/")

@main.route("/users/create", methods=["GET", "POST"])
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

@main.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


@main.route("/jars", methods=["GET", "POST"])
@login_required
def jars():

    jars = get_jars()

    if request.method =="POST":
        jarName = request.form.get("name")
        if request.files:

            jarFile = request.files["jarFile"]

            if save_jar(jarFile, jarName):
                print("Jar saved and added to database")
                return redirect(request.url)
            else:
                return redirect(request.url)
            

    return render_template("jars.html", jar_data=jars)

@main.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect to homepage/login
    return redirect("/")

















