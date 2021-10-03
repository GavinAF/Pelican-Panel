import os
import requests
import urllib.parse
from flask import redirect, render_template, request, session
from functools import wraps
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session
from config import db_info, tables_sql

def check_database():
    try:
        conn = psycopg2.connect(
            host = db_info['host'],
            user = db_info['username'],
            password = db_info['password'],
            port = db_info['port'])

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        select_data = '''SELECT datname FROM pg_database'''

        cur.execute(select_data)
        databases = cur.fetchall()

        if db_info['database'] in databases:
            print("Database already exists")
            return True

        # Create the database
        cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_info['database'])))
        cur.close()
        conn.close()

        # Connect to new database
        conn = psycopg2.connect(
            host = db_info['host'],
            database= db_info['database'],
            user = db_info['username'],
            password = db_info['password'],
            port = db_info['port'])
        cur = conn.cursor()

        # Create the tables & columns
        for command in tables_sql:
            cur.execute(command)
        cur.close()
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while checking database", error)
        return False
    finally:
        # Closing database connection.
            if(conn):
                cur.close()
                conn.close()
                print("PostgreSQL connection is closed")

            return True

def login_user(username, password):

    # Check username in database
    try:
        conn = psycopg2.connect(
            host = db_info['host'],
            database= db_info['database'],
            user = db_info['username'],
            password = db_info['password'],
            port = db_info['port'])

        cur = conn.cursor()

        select_username_query = '''SELECT * FROM users WHERE username = %s'''

        cur.execute(select_username_query, (username, ))
        rows = cur.fetchall()
        conn.commit()
        print("Selected user data from database")

        if len(rows) != 1 or not check_password_hash(rows[0][2], password):
            return False

        session["user_id"] = rows[0][0]
        session["username"] = username

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while selecting user data from database", error)
        return False
    finally:
        #closing database connection.
            if(conn):
                cur.close()
                conn.close()
                print("PostgreSQL connection is closed")
                
            return True

def create_user(username, password, email):
    # Insert user into database
    try:
        conn = psycopg2.connect(
            host = db_info['host'],
            database= db_info['database'],
            user = db_info['username'],
            password = db_info['password'],
            port = db_info['port'])

        cur = conn.cursor()
        
        # print(username, password, email)
        insert_user_query = '''INSERT INTO users (username, passhash, email) VALUES (%s, %s, %s) RETURNING id'''

        cur.execute(insert_user_query, (username, generate_password_hash(password), email))
        rows = cur.fetchall()
        conn.commit()
        print("Inserted user into database")

        session["user_id"] = rows[0][0]
        session["username"] = username

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while inserting user into database", error)
        return False
    finally:
        # Closing database connection.
            if(conn):
                cur.close()
                conn.close()
                print("PostgreSQL connection is closed")

            return True

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

def get_servers(userid):

    # Get servers from database
    try:
        conn = psycopg2.connect(
            host = db_info['host'],
            database= db_info['database'],
            user = db_info['username'],
            password = db_info['password'],
            port = db_info['port'])

        cur = conn.cursor()

        select_servers_query = '''SELECT * FROM servers'''

        cur.execute(select_servers_query)
        rows = cur.fetchall()
        conn.commit()
        print("Selected servers from database")

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while selecting server data from database", error)
        return False
    finally:
        # Closing database connection
            if(conn):
                cur.close()
                conn.close()
                print("PostgreSQL connection is closed")
                
            return rows

def create_server(name, memory, slots, port, jar):
    # Insert server into database

    server_id = None

    try:
        conn = psycopg2.connect(
            host = db_info['host'],
            database= db_info['database'],
            user = db_info['username'],
            password = db_info['password'],
            port = db_info['port'])

        cur = conn.cursor()
        
        insert_server_query = '''INSERT INTO servers (name, memory, slots, port, jar) VALUES (%s, %s, %s, %s, %s) RETURNING server_id'''

        cur.execute(insert_server_query, (name, memory, slots, port, jar))
        server_id = cur.fetchone()[0]
        conn.commit()
        print("Inserted server into database")

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while inserting server into database", error)
        return False
    finally:
        # Closing database connection.
            if(conn):
                cur.close()
                conn.close()
                print("PostgreSQL connection is closed")

            return server_id

def remove_server(server_id):
    # Remove server from database
    try:
        conn = psycopg2.connect(
            host = db_info['host'],
            database= db_info['database'],
            user = db_info['username'],
            password = db_info['password'],
            port = db_info['port'])

        cur = conn.cursor()
        
        # print(username, password, email)
        remove_server_query = '''DELETE FROM servers WHERE server_id = %s'''

        user_id = session["user_id"]

        cur.execute(remove_server_query, (server_id, ))
        conn.commit()
        print("Removed server from database")

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while removing server from database", error)
        # return False
    finally:
        # Closing database connection.
            if(conn):
                cur.close()
                conn.close()
                print("PostgreSQL connection is closed")

            # return True

def get_users():

    # Get users from database
    try:
        conn = psycopg2.connect(
            host = db_info['host'],
            database= db_info['database'],
            user = db_info['username'],
            password = db_info['password'],
            port = db_info['port'])

        cur = conn.cursor()

        select_servers_query = '''SELECT * FROM users'''

        cur.execute(select_servers_query)
        rows = cur.fetchall()
        conn.commit()
        print("Selected users from database")

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while selecting user data from database", error)
        return False
    finally:
        # Closing database connection
            if(conn):
                cur.close()
                conn.close()
                print("PostgreSQL connection is closed")
                
            return rows

def remove_user(user_id):
    # Remove user from database
    try:
        conn = psycopg2.connect(
            host = db_info['host'],
            database= db_info['database'],
            user = db_info['username'],
            password = db_info['password'],
            port = db_info['port'])

        cur = conn.cursor()
        
        # print(username, password, email)
        remove_server_query = '''DELETE FROM users WHERE id = %s'''

        cur.execute(remove_server_query, (user_id, ))
        conn.commit()
        print("Removed user from database")

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while removing user from database", error)
        # return False
    finally:
        # Closing database connection.
            if(conn):
                cur.close()
                conn.close()
                print("PostgreSQL connection is closed")

            # return True

def create_user_panel(username, password, email):
    # Insert user into database
    try:
        conn = psycopg2.connect(
            host = db_info['host'],
            database= db_info['database'],
            user = db_info['username'],
            password = db_info['password'],
            port = db_info['port'])

        cur = conn.cursor()
        
        # print(username, password, email)
        insert_user_query = '''INSERT INTO users (username, passhash, email) VALUES (%s, %s, %s)'''

        cur.execute(insert_user_query, (username, generate_password_hash(password), email))
        conn.commit()
        print("Inserted user into database")

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while inserting user into database", error)
        return False
    finally:
        # Closing database connection.
            if(conn):
                cur.close()
                conn.close()
                print("PostgreSQL connection is closed")

            return True