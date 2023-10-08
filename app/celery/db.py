import logging
from typing import Optional

import mysql.connector
from mysql.connector.pooling import PooledMySQLConnection

from app.config import DB_CONFIG, POOL_SIZE

logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(self):
        logger.info("Initializing connector")
        self.pool_size = POOL_SIZE
        self.pool_name = "globant_pool"
        self.db_config = DB_CONFIG
        self.conn = self.connect()

    def connect(self) -> Optional[PooledMySQLConnection]:

        try:

            conn = mysql.connector.connect(
                pool_name=self.pool_name,
                pool_size=self.pool_size,
                **self.db_config
            )
            logger.info("Connection pool created successfully")

            return conn

        except mysql.connector.Error as e:
            logger.error("Error:", e)
            return None

    def is_connected(self) -> bool:
        return self.conn.is_connected()

    def check_connection(self):
        logger.info("Checking connection")
        if self.is_connected() is False:
            logger.info("Connection lost, Reconnecting...")
            self.connect()
