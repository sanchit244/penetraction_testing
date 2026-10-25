# MySQL Database Setup Script

"""
Run this script to create the database for VulnScanner

Prerequisites:
1. MySQL installed and running
2. MySQL credentials configured in .env file

Usage:
python setup_database.py
"""

import pymysql
import sys

# Database configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Sanchit@8984"
DB_NAME = "vulnscanner_db"

def create_database():
    """Create the VulnScanner database"""
    try:
        # Connect to MySQL server
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )

        cursor = connection.cursor()

        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{DB_NAME}' created successfully!")

        # Switch to the database
        cursor.execute(f"USE {DB_NAME}")

        # Grant privileges (if needed)
        cursor.execute(f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")

        connection.commit()
        cursor.close()
        connection.close()

        print(f"✅ Database setup completed successfully!")
        print(f"📊 Database: {DB_NAME}")
        print(f"👤 User: {DB_USER}")
        print(f"🔗 Connection: mysql+pymysql://{DB_USER}:****@{DB_HOST}/{DB_NAME}")

        return True

    except pymysql.Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def verify_connection():
    """Verify database connection"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()

        print(f"\n✅ Connection successful!")
        print(f"📌 MySQL Version: {version[0]}")

        cursor.close()
        connection.close()
        return True

    except pymysql.Error as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("VulnScanner - MySQL Database Setup")
    print("=" * 60)
    print()

    # Create database
    if create_database():
        print()
        # Verify connection
        verify_connection()
        print()
        print("=" * 60)
        print("🎉 Setup Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Run: cd backend")
        print("2. Run: pip install -r requirements.txt")
        print("3. Run: python main.py")
        print()
    else:
        print("\n❌ Setup failed. Please check your MySQL credentials.")
        sys.exit(1)
