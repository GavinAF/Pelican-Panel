import rpyc
import time
import os
import shutil
import wexpect
from webapp.extensions import db
from webapp.models import Server as ServerModel
from webapp.models import Jar
from webapp import app

class Server():

    instances={}

    def __init__(self, server_id):
        self.server_id = server_id
        self.p = None
        self.jar = None
        self.memory = None
        self.start_command = None

        self.populate()
        Server.instances[server_id] = self

    def populate(self):

        try:

            with app.app_context():
                select_server = ServerModel.query.filter_by(id=self.server_id).one()
                jarFile = Jar.query.filter_by(id=select_server.jar).one()

                attrs = vars(self)

                self.jar = jarFile.file
                self.memory = select_server.memory
                            

        except Exception as e:
            print(e)

        finally:
            pass

    def start(self):

        try:
            self.start_command = f"java -Xms1024M -Xmx{self.memory}M -jar ../../jars/{self.jar} nogui"

            self.p = wexpect.spawn(self.start_command, cwd=f"servers/{self.server_id}")


        except Exception as e:
            print(e)

        if self.p is not None:
            print("STARTING: P is not None")
            return True
        else:
            return False   

    def send_command(self, command):
        if self.p is not None:
            self.p.sendline(command)
            return True
        else:
            return False

    def stop(self):
        if self.p.isalive():
            self.p.sendline("stop")
            while self.p.isalive():
                time.sleep(1)
            return True
        else:
            print("self.p is not alive")
            return False

    def restart(self):
        if self.p.isalive():
            self.p.sendline("stop")
            while self.p.isalive():
                time.sleep(1)

            self.p = wexpect.spawn(self.start_command, cwd=f"servers/{self.server_id}")
            
            return True
        else:
            print("self.p is not alive")
            return False


# Is there an instance already
def checkClass(server_id):

    current_id = str(server_id)

    if current_id in Server.instances:
        return True
    else:
        return False

# Is the server running
def checkAlive(server_id):
    server_id = str(server_id)

    # If server instance exists, does the console exist? If so, return true
    if checkClass(server_id):
        #server = Server(server_id)
        server = Server.instances[server_id]
        if server.p is not None:
            print(f"Server {server_id} is not none")
            if server.p.isalive():
                print(f"server {server_id} is not alive")
                return True
        else:
            print(f"Server {server_id} is not alive")
            return False

    return False

class MyService(rpyc.Service):

    def exposed_create_server(self, server_id, port):

        print(f"Creating server {server_id}")

        # Create folder
        os.makedirs(f"servers/{server_id}")

        # Create eula file
        with open(f"servers/{server_id}/eula.txt", "w") as file:
            file.write("eula=true")

        # Create server.properties with port
        with open(f"servers/{server_id}/server.properties", "w") as file:
            file.write(f"query.port={port}\nserver-port={port}")

        # Create Server class instance 
        server = Server(server_id)

        return True


    def exposed_remove_server(self, server_id):
        print(f"Removing server {server_id}")

        # Check if folder exists then delete it
        if os.path.isdir(f"servers/{server_id}"):
            shutil.rmtree(f"servers/{server_id}")
            return True
        else:
            return False


    def exposed_start_server(self, server_id):

        # If server instance exists, use it otherwise create one
        if checkClass(server_id):
            server = Server.instances[server_id]
        else:
            server = Server(server_id)

        # Is the server running already?
        if checkAlive(server_id):
            print(f"Server {server_id} is already started")
            return False

        print("\nStarting Server " + server_id)
        return server.start()

    def exposed_stop_server(self, server_id):

        server_id = str(server_id)

        server = Server.instances[server_id]

        print("\nStopping Server " + server_id)

        if server.stop():
            del Server.instances[server_id]
            return True
        else:
            return False

    def exposed_restart_server(self, server_id):

        server_id = str(server_id)

        server = Server.instances[server_id]

        print("\nRestarting Server " + server_id)

        if server.restart():
            return True
        else:
            return False


    def exposed_active_servers(self, ):
        print("The Active Servers Are: ")
        print(Server.instances)
        return True

    def exposed_is_active(self, server_id):

        print(f"Checking if {server_id} is active")

        if checkAlive(server_id):
            print(f"{server_id} is active")
            return True
        else:
            print(f"{server_id} is not active")
            return False


from rpyc.utils.server import ThreadedServer
from threading import Thread
server = ThreadedServer(MyService, port = 42069)
t = Thread(target = server.start)
t.daemon = True
t.start()

print("External Server Started Successfully!\nWaiting for input...")

while True: 
    time.sleep(1)
