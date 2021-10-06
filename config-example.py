# Database Info
db_info = dict(
    username = "postgres",
    password = "YourPasswordHere",
    host = "127.0.0.1",
    port = "5432",
    database = "pelican",
)

tables_sql = (
    '''CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        passhash VARCHAR(255) NOT NULL,
        email VARCHAR(255)
        )
        ''',

    '''CREATE TABLE servers (
        server_id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        memory SERIAL NOT NULL,
        slots SERIAL NOT NULL,
        port SERIAL NOT NULL,
        jar VARCHAR(255) NOT NULL
        )
        '''
)