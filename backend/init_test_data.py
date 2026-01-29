"""
Initialize database with test data for Adult TikTok platform
"""
import sys
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database_mysql import get_db_connection, init_database
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_users():
    """Create test users including an admin"""
    init_database()
    
    users = [
        {
            'id': str(uuid.uuid4()),
            'username': 'admin',
            'email': 'admin@adulttok.com',
            'password': 'admin123',
            'display_name': 'Admin User',
            'bio': 'Platform Administrator',
            'is_admin': True,
            'is_creator': True,
            'is_verified': True
        },
        {
            'id': str(uuid.uuid4()),
            'username': 'creator1',
            'email': 'creator1@adulttok.com',
            'password': 'creator123',
            'display_name': 'Sexy Creator',
            'bio': '🔥 Premium content creator 💋 Subscribe for exclusive content',
            'is_admin': False,
            'is_creator': True,
            'is_verified': True
        },
        {
            'id': str(uuid.uuid4()),
            'username': 'user1',
            'email': 'user1@adulttok.com',
            'password': 'user123',
            'display_name': 'Regular User',
            'bio': 'Just here to enjoy content',
            'is_admin': False,
            'is_creator': False,
            'is_verified': False
        }
    ]
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for user in users:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (user['username'],))
            existing = cursor.fetchone()
            
            if not existing:
                hashed_password = pwd_context.hash(user['password'])
                cursor.execute("""
                    INSERT INTO users 
                    (id, username, email, password_hash, display_name, bio, is_admin, is_creator, is_verified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user['id'],
                    user['username'],
                    user['email'],
                    hashed_password,
                    user['display_name'],
                    user['bio'],
                    user['is_admin'],
                    user['is_creator'],
                    user['is_verified']
                ))
                print(f"✅ Created user: {user['username']} (password: {user['password']})")
            else:
                print(f"⚠️  User {user['username']} already exists")
        
        conn.commit()
        cursor.close()
    
    print("\n" + "="*60)
    print("TEST USERS CREATED SUCCESSFULLY!")
    print("="*60)
    print("\nLogin credentials:")
    print("  Admin:")
    print("    Username: admin")
    print("    Password: admin123")
    print("\n  Creator:")
    print("    Username: creator1")
    print("    Password: creator123")
    print("\n  Regular User:")
    print("    Username: user1")
    print("    Password: user123")
    print("="*60)

if __name__ == "__main__":
    try:
        create_test_users()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
