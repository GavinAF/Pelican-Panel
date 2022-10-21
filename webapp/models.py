from webapp.extensions import db

# Users Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    passhash = db.Column(db.Text)

    def __repr__(self):
        return f"<User {self.username}>"

# Servers table
class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    memory = db.Column(db.Integer, nullable=False)
    slots = db.Column(db.Integer, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    jar = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Server {self.name}>"

# Jars table
class Jar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    file = db.Column(db.String(100), unique=True, nullable=False)