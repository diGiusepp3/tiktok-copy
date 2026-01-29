import mysql.connector
from mysql.connector import pooling, Error
import os
import logging
from contextlib import contextmanager
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# MySQL connection configuration from environment variables
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'port': int(os.environ.get('MYSQL_PORT', 3306)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DATABASE', 'adult_tiktok')
}

# Connection pool
connection_pool = None

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    connection = None
    try:
        connection = connection_pool.get_connection()
        yield connection
    except Error as err:
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
        database_name = temp_config.pop('database')
        
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        cursor.execute(f"USE {database_name}")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                display_name VARCHAR(100),
                bio TEXT,
                avatar_url VARCHAR(500),
                is_admin BOOLEAN DEFAULT FALSE,
                is_creator BOOLEAN DEFAULT FALSE,
                is_verified BOOLEAN DEFAULT FALSE,
                followers_count INT DEFAULT 0,
                following_count INT DEFAULT 0,
                likes_count INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_email (email)
            )
        """)
        
        # Create posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                type ENUM('image', 'video') NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                thumbnail_path VARCHAR(500),
                caption TEXT,
                likes_count INT DEFAULT 0,
                comments_count INT DEFAULT 0,
                shares_count INT DEFAULT 0,
                views_count INT DEFAULT 0,
                is_public BOOLEAN DEFAULT TRUE,
                subscribers_only BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at DESC),
                INDEX idx_is_public (is_public)
            )
        """)
        
        # Create subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id VARCHAR(36) PRIMARY KEY,
                subscriber_user_id VARCHAR(36) NOT NULL,
                creator_user_id VARCHAR(36) NOT NULL,
                price DECIMAL(10, 2) DEFAULT 0.00,
                status ENUM('active', 'expired', 'cancelled') DEFAULT 'active',
                expires_at TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (subscriber_user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (creator_user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_subscription (subscriber_user_id, creator_user_id),
                INDEX idx_subscriber (subscriber_user_id),
                INDEX idx_creator (creator_user_id),
                INDEX idx_status (status)
            )
        """)
        
        # Create likes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                post_id VARCHAR(36) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                UNIQUE KEY unique_like (user_id, post_id),
                INDEX idx_user_id (user_id),
                INDEX idx_post_id (post_id)
            )
        """)
        
        # Create comments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                post_id VARCHAR(36) NOT NULL,
                content TEXT NOT NULL,
                likes_count INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                INDEX idx_post_id (post_id),
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at DESC)
            )
        """)
        
        # Create follows table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS follows (
                id VARCHAR(36) PRIMARY KEY,
                follower_id VARCHAR(36) NOT NULL,
                following_id VARCHAR(36) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_follow (follower_id, following_id),
                INDEX idx_follower (follower_id),
                INDEX idx_following (following_id)
            )
        """)
        
        # Create admin_scrapers_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_scrapers_log (
                id VARCHAR(36) PRIMARY KEY,
                scraper_name VARCHAR(100) NOT NULL,
                status ENUM('running', 'completed', 'failed') NOT NULL,
                items_scraped INT DEFAULT 0,
                error_message TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                INDEX idx_scraper_name (scraper_name),
                INDEX idx_status (status),
                INDEX idx_started_at (started_at DESC)
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Now create connection pool with database
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="adult_tiktok_pool",
            pool_size=10,
            pool_reset_session=True,
            **MYSQL_CONFIG
        )
        
        logger.info("Adult TikTok database initialized successfully")
        return True
    except Error as err:
        logger.error(f"Error initializing database: {err}")
        return False

def get_connection_pool():
    """Get the connection pool"""
    return connection_pool
