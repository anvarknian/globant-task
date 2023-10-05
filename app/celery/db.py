import logging

from psycopg2 import pool

logger = logging.getLogger(__name__)

db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=100,
    database="globant",
    user="postgres",
    password="postgres",
    host="postgres",
    port="5432"
)


def get_connection():
    try:
        connection = db_pool.getconn()
        return connection
    except Exception as e:
        logger.error("Error getting a database connection: %s", str(e))
        raise
