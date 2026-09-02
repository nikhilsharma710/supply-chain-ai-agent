import psycopg2

from app.config import settings

def get_connection():
    '''Open a new database connection from the application configuration.'''

    return psycopg2.connect(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_username,
        password=settings.database_password,
    )
