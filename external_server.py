from config import db_info
import rpyc
import time
import psycopg2
import os
import subprocess
import wexpect
from psycopg2.extras import RealDictCursor

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

        self.conn = psycopg2.connect(
            host = db_info['host'],
            database= db_info['database'],
            user = db_info['username'],
            password = db_info['password'],
            port = db_info['port'])

        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

        sql_query = "SELECT * FROM servers WHERE server_id=%s"

        self.cur.execute(sql_query, (self.server_id,))
        row = self.cur.fetchone()

        attrs = vars(self)

        for name in attrs.keys():
            for col_name in row:
                if col_name == name:
                    setattr(self, name, row[name])

        # Close cursor & connection
        self.cur.close()
        self.conn.close()

    def start(self):
        self.start_command = f"java -Xms1024M -Xmx{self.memory}M -jar ../../jars/{self.jar}.jar nogui"

        self.p = wexpect.spawn(self.start_command, cwd=f"servers/{self.server_id}")

        if self.p.isalive():
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

def checkClass(server_id):

    current_id = str(server_id)

    if current_id in Server.instances:
        return True
    else:
        return False

def checkAlive(server_id):
    server_id = str(server_id)
    server = Server(server_id)
    if server.p.isalive():
        return True
    else:
        return False

class MyService(rpyc.Service):

    def exposed_create_server(self, server_id):

        print(f"Creating server {server_id}")

        # Create folder and eula file
        os.makedirs(f"servers/{server_id}")
        with open(f"servers/{server_id}/eula.txt", "w") as file:
            file.write("eula=true")

        # Create Server class instance 
        server = Server(server_id)

        return True

    def exposed_start_server(self, server_id):

        if checkClass(server_id):
            print(f"Server {server_id} is already started")
            return True

        server = Server(server_id)
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

        if checkClass(server_id):
            print(f"{server_id} is active")
            return True
        else:
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
