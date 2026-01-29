import mysql.connector
from mysql.connector import pooling
import os
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# MySQL connection configuration
MYSQL_CONFIG = {
    'host': 'mgielen.zapto.org',
    'port': 3306,
    'user': 'matthias',
    'password': 'DigiuSeppe2018___',
    'database': 'chatgpt_clone'
}

# Connection pool will be created after database initialization
connection_pool = None

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    connection = None
    try:
        connection = connection_pool.get_connection()
        yield connection
    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()

def init_database():
    """Initialize database and create tables if they don't exist"""
    global connection_pool
    try:
        # First, connect without database to create it
        temp_config = MYSQL_CONFIG.copy()
        del temp_config['database']
        
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS chatgpt_clone")
        cursor.execute("USE chatgpt_clone")
        
        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id VARCHAR(36) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id VARCHAR(36) PRIMARY KEY,
                conversation_id VARCHAR(36) NOT NULL,
                role ENUM('user', 'assistant') NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                INDEX idx_conversation_id (conversation_id)
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Now create connection pool
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="chatgpt_pool",
            pool_size=5,
            pool_reset_session=True,
            **MYSQL_CONFIG
        )
        
        logger.info("Database initialized successfully")
        return True
    except mysql.connector.Error as err:
        logger.error(f"Error initializing database: {err}")
        return False
