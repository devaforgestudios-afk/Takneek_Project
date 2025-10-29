from contextlib import contextmanager
from mysql.connector import Error, pooling


def create_users_table(pool):
    """Creates the users table if it doesn't exist."""
    try:
        with pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
                """)
                print("Users table created or already exists.")
    except Error as e:
        print(f"Error creating users table: {e}")

def create_artworks_table(pool):
    """Creates the artworks table if it doesn't exist."""
    try:
        with pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS artworks (
                    id VARCHAR(255) PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    category VARCHAR(255) NOT NULL,
                    material VARCHAR(255) NOT NULL,
                    time_spent VARCHAR(255),
                    description TEXT NOT NULL,
                    price FLOAT,
                    files JSON,
                    created_at DATETIME,
                    status VARCHAR(255),
                    views INT DEFAULT 0,
                    likes INT DEFAULT 0,
                    feedback JSON,
                    FOREIGN KEY (user_email) REFERENCES users(email)
                )
                """)
                print("Artworks table created or already exists.")
    except Error as e:
        print(f"Error creating artworks table: {e}")

def drop_artworks_table(pool):
    """Drops the artworks table if it exists."""
    try:
        with pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS artworks")
                print("Artworks table dropped if it existed.")
    except Error as e:
        print(f"Error dropping artworks table: {e}")

def create_community_posts_table(pool):
    """Creates the community_posts table if it doesn't exist."""
    try:
        with pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS community_posts (
                    id VARCHAR(255) PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    image VARCHAR(255),
                    timestamp DATETIME,
                    FOREIGN KEY (user_email) REFERENCES users(email)
                )
                """)
                print("Community posts table created or already exists.")
    except Error as e:
        print(f"Error creating community_posts table: {e}")

def create_contact_table(pool):
    """Creates the contact table if it doesn't exist."""
    try:
        with pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS contact (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    subject VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """)
                print("Contact table created or already exists.")
    except Error as e:
        print(f"Error creating contact table: {e}")
