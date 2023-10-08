import os
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv

load_dotenv()

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")

DATABASE_URL = os.environ.get("DATABASE_URL", "jdbc:mysql://mysql:mysql@mysql:5432/globant")

POOL_SIZE = int(os.environ.get("POOL_SIZE", 5))

parsed_url = urlparse(DATABASE_URL)

DB_HOST = parsed_url.hostname
DB_PORT = int(parsed_url.port)
DB_USER = parsed_url.username
DB_PASSWORD = parsed_url.password
DB_DATABASE = parsed_url.path.lstrip('/')

SSLACCEPT = parse_qs(parsed_url.query).get('ssl-mode', [''])[0]

DB_CONFIG = {
    "host": DB_HOST,
    "port": DB_PORT if DB_PORT else 443,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_DATABASE,
    # "ssl-mode": SSLACCEPT,
}
