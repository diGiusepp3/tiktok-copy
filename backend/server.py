from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import pooling
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import subprocess
import asyncio
import json
import aiofiles
import yt_dlp
import shutil

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MySQL connection pool
db_config = {
    "host": os.environ.get('MYSQL_HOST', 'localhost'),
    "port": int(os.environ.get('MYSQL_PORT', 3306)),
    "user": os.environ.get('MYSQL_USER'),
    "password": os.environ.get('MYSQL_PASSWORD'),
    "database": os.environ.get('MYSQL_DATABASE', 'clone_app'),
}

connection_pool = None

def ensure_database_exists():
    """Create database if it doesn't exist"""
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Database '{db_config['database']}' ensured")
    except mysql.connector.Error as err:
        logger.error(f"Error creating database: {err}")

def get_db_connection():
    global connection_pool
    if connection_pool is None:
        ensure_database_exists()
        try:
            connection_pool = pooling.MySQLConnectionPool(
                pool_name="clone_pool",
                pool_size=5,
                pool_reset_session=True,
                **db_config
            )
        except mysql.connector.Error as err:
            logger.error(f"Error creating connection pool: {err}")
            raise HTTPException(status_code=500, detail="Database connection failed")
    return connection_pool.get_connection()

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'fallback_secret_key')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 72

# Media paths
MEDIA_BASE_PATH = Path(os.environ.get('MEDIA_BASE_PATH', '/mnt/sata_m2'))
LEGACY_MEDIA_PATH = Path(os.environ.get('LEGACY_MEDIA_PATH', '/mnt/bigdisk/images'))

# Create the main app
app = FastAPI(title="Clone App API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    is_creator: bool
    created_at: str

class CreatorProfile(BaseModel):
    id: str
    user_id: str
    username: str
    display_name: str
    avatar_url: Optional[str]
    cover_url: Optional[str]
    bio: Optional[str]
    subscriber_count: int
    post_count: int
    media_count: int

class MediaItem(BaseModel):
    id: str
    creator_id: str
    file_path: str
    file_name: str
    file_type: str  # image, video
    thumbnail_url: Optional[str]
    duration: Optional[float]
    width: Optional[int]
    height: Optional[int]
    file_size: int
    category: str  # Posts, Stories, Messages
    created_at: str
    likes: int = 0
    views: int = 0

class ScraperTask(BaseModel):
    url: str
    output_path: Optional[str] = None

class CLICommand(BaseModel):
    command: str
    cwd: Optional[str] = None

class FileOperation(BaseModel):
    source: str
    destination: str
    operation: str  # move, copy, delete

# ==================== AUTH HELPERS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== DATABASE INITIALIZATION ====================

def init_database():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                display_name VARCHAR(100),
                avatar_url TEXT,
                cover_url TEXT,
                bio TEXT,
                is_creator BOOLEAN DEFAULT FALSE,
                subscriber_count INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Media items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media_items (
                id VARCHAR(36) PRIMARY KEY,
                creator_id VARCHAR(36),
                file_path TEXT NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_type VARCHAR(20) NOT NULL,
                thumbnail_url TEXT,
                duration FLOAT,
                width INT,
                height INT,
                file_size BIGINT DEFAULT 0,
                category VARCHAR(50),
                likes INT DEFAULT 0,
                views INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id VARCHAR(36) PRIMARY KEY,
                subscriber_id VARCHAR(36),
                creator_id VARCHAR(36),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subscriber_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_subscription (subscriber_id, creator_id)
            )
        """)
        
        # Scraper tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraper_tasks (
                id VARCHAR(36) PRIMARY KEY,
                url TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                output_path TEXT,
                result TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL
            )
        """)
        
        # Likes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36),
                media_id VARCHAR(36),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (media_id) REFERENCES media_items(id) ON DELETE CASCADE,
                UNIQUE KEY unique_like (user_id, media_id)
            )
        """)
        
        conn.commit()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register")
async def register(user: UserCreate):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", (user.email, user.username))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="User already exists")
        
        user_id = str(uuid.uuid4())
        password_hash = hash_password(user.password)
        
        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash, display_name)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, user.username, user.email, password_hash, user.display_name or user.username))
        
        conn.commit()
        
        token = create_token(user_id, user.email)
        return {
            "token": token,
            "user": {
                "id": user_id,
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name or user.username
            }
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (credentials.email,))
        user = cursor.fetchone()
        
        if not user or not verify_password(credentials.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_token(user['id'], user['email'])
        return {
            "token": token,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "display_name": user['display_name'],
                "avatar_url": user['avatar_url'],
                "is_creator": user['is_creator']
            }
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@api_router.get("/auth/me")
async def get_current_user(payload: dict = Depends(verify_token)):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, username, email, display_name, avatar_url, bio, is_creator, created_at FROM users WHERE id = %s", (payload['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user['created_at'] = user['created_at'].isoformat() if user['created_at'] else None
        return user
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ==================== CREATOR/PROFILE ROUTES ====================

@api_router.get("/creators")
async def get_creators(limit: int = 20, offset: int = 0):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, username, display_name, avatar_url, cover_url, bio, subscriber_count,
                   (SELECT COUNT(*) FROM media_items WHERE creator_id = users.id) as media_count
            FROM users 
            WHERE is_creator = TRUE
            ORDER BY subscriber_count DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        creators = cursor.fetchall()
        return {"creators": creators, "total": len(creators)}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@api_router.get("/creators/{username}")
async def get_creator_profile(username: str):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, username, display_name, avatar_url, cover_url, bio, subscriber_count, created_at,
                   (SELECT COUNT(*) FROM media_items WHERE creator_id = users.id) as media_count,
                   (SELECT COUNT(*) FROM media_items WHERE creator_id = users.id AND category = 'Posts') as post_count
            FROM users 
            WHERE username = %s
        """, (username,))
        
        creator = cursor.fetchone()
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        creator['created_at'] = creator['created_at'].isoformat() if creator['created_at'] else None
        return creator
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@api_router.post("/creators/{creator_id}/subscribe")
async def subscribe_to_creator(creator_id: str, payload: dict = Depends(verify_token)):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sub_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO subscriptions (id, subscriber_id, creator_id)
            VALUES (%s, %s, %s)
        """, (sub_id, payload['user_id'], creator_id))
        
        cursor.execute("UPDATE users SET subscriber_count = subscriber_count + 1 WHERE id = %s", (creator_id,))
        conn.commit()
        
        return {"message": "Subscribed successfully"}
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="Already subscribed")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ==================== MEDIA/FEED ROUTES ====================

@api_router.get("/feed")
async def get_feed(limit: int = 10, offset: int = 0, file_type: Optional[str] = None):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT m.*, u.username, u.display_name, u.avatar_url as creator_avatar
            FROM media_items m
            JOIN users u ON m.creator_id = u.id
        """
        params = []
        
        if file_type:
            query += " WHERE m.file_type = %s"
            params.append(file_type)
        
        query += " ORDER BY m.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        for item in items:
            item['created_at'] = item['created_at'].isoformat() if item['created_at'] else None
        
        return {"items": items, "total": len(items)}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@api_router.get("/creators/{creator_id}/media")
async def get_creator_media(creator_id: str, category: Optional[str] = None, limit: int = 50, offset: int = 0):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM media_items WHERE creator_id = %s"
        params = [creator_id]
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        for item in items:
            item['created_at'] = item['created_at'].isoformat() if item['created_at'] else None
        
        return {"items": items, "total": len(items)}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@api_router.post("/media/{media_id}/like")
async def like_media(media_id: str, payload: dict = Depends(verify_token)):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        like_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO likes (id, user_id, media_id)
            VALUES (%s, %s, %s)
        """, (like_id, payload['user_id'], media_id))
        
        cursor.execute("UPDATE media_items SET likes = likes + 1 WHERE id = %s", (media_id,))
        conn.commit()
        
        return {"message": "Liked"}
    except mysql.connector.IntegrityError:
        # Unlike
        cursor.execute("DELETE FROM likes WHERE user_id = %s AND media_id = %s", (payload['user_id'], media_id))
        cursor.execute("UPDATE media_items SET likes = likes - 1 WHERE id = %s", (media_id,))
        conn.commit()
        return {"message": "Unliked"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@api_router.post("/media/{media_id}/view")
async def increment_view(media_id: str):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE media_items SET views = views + 1 WHERE id = %s", (media_id,))
        conn.commit()
        return {"message": "View recorded"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ==================== FILE MANAGEMENT ROUTES ====================

@api_router.get("/files/scan")
async def scan_legacy_media(path: Optional[str] = None, limit: int = 100, offset: int = 0):
    """Scan the legacy media folder structure"""
    base_path = Path(path) if path else LEGACY_MEDIA_PATH
    
    if not base_path.exists():
        return {"creators": [], "message": f"Path {base_path} does not exist"}
    
    creators = []
    try:
        for creator_dir in list(base_path.iterdir())[offset:offset+limit]:
            if creator_dir.is_dir():
                creator_info = {
                    "name": creator_dir.name,
                    "path": str(creator_dir),
                    "categories": {}
                }
                
                for category in ['Messages', 'Posts', 'Stories']:
                    cat_path = creator_dir / category
                    if cat_path.exists():
                        media_count = {"images": 0, "videos": 0}
                        for media_type in ['Images', 'Videos']:
                            type_path = cat_path / media_type
                            if type_path.exists():
                                files = list(type_path.glob('*'))
                                if media_type == 'Images':
                                    media_count['images'] = len(files)
                                else:
                                    media_count['videos'] = len(files)
                        creator_info['categories'][category] = media_count
                
                creators.append(creator_info)
    except PermissionError as e:
        logger.error(f"Permission error scanning {base_path}: {e}")
    
    return {"creators": creators, "total": len(creators), "base_path": str(base_path)}

@api_router.get("/files/browse")
async def browse_files(path: str = "/", limit: int = 100, offset: int = 0):
    """Browse any directory on the server"""
    target_path = Path(path)
    
    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")
    
    items = []
    try:
        all_items = sorted(target_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        for item in all_items[offset:offset+limit]:
            item_info = {
                "name": item.name,
                "path": str(item),
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else 0,
                "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
            }
            if item.is_file():
                ext = item.suffix.lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    item_info['type'] = 'image'
                elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
                    item_info['type'] = 'video'
                else:
                    item_info['type'] = 'file'
            items.append(item_info)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return {"items": items, "path": str(target_path), "parent": str(target_path.parent)}

@api_router.post("/files/import")
async def import_creator_media(creator_name: str, background_tasks: BackgroundTasks, payload: dict = Depends(verify_token)):
    """Import a creator's media from legacy path to database"""
    creator_path = LEGACY_MEDIA_PATH / creator_name
    
    if not creator_path.exists():
        raise HTTPException(status_code=404, detail="Creator folder not found")
    
    # Create or get creator user
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id FROM users WHERE username = %s", (creator_name,))
        user = cursor.fetchone()
        
        if not user:
            user_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, display_name, is_creator)
                VALUES (%s, %s, %s, %s, %s, TRUE)
            """, (user_id, creator_name, f"{creator_name}@import.local", hash_password('imported'), creator_name))
            conn.commit()
        else:
            user_id = user['id']
        
        # Queue background import task
        background_tasks.add_task(import_media_files, user_id, creator_path)
        
        return {"message": f"Import started for {creator_name}", "user_id": user_id}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

async def import_media_files(user_id: str, creator_path: Path):
    """Background task to import media files"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for category in ['Posts', 'Stories', 'Messages']:
            cat_path = creator_path / category
            if not cat_path.exists():
                continue
            
            for media_type in ['Images', 'Videos']:
                type_path = cat_path / media_type
                if not type_path.exists():
                    continue
                
                file_type = 'image' if media_type == 'Images' else 'video'
                
                for file_path in type_path.glob('*'):
                    if file_path.is_file():
                        media_id = str(uuid.uuid4())
                        try:
                            cursor.execute("""
                                INSERT INTO media_items (id, creator_id, file_path, file_name, file_type, category, file_size)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (media_id, user_id, str(file_path), file_path.name, file_type, category, file_path.stat().st_size))
                        except Exception as e:
                            logger.error(f"Error importing {file_path}: {e}")
        
        conn.commit()
        logger.info(f"Import completed for user {user_id}")
    except Exception as e:
        logger.error(f"Import error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@api_router.post("/files/move")
async def move_files(operation: FileOperation, payload: dict = Depends(verify_token)):
    """Move, copy, or delete files"""
    source = Path(operation.source)
    destination = Path(operation.destination)
    
    if not source.exists():
        raise HTTPException(status_code=404, detail="Source not found")
    
    try:
        if operation.operation == 'move':
            shutil.move(str(source), str(destination))
        elif operation.operation == 'copy':
            if source.is_dir():
                shutil.copytree(str(source), str(destination))
            else:
                shutil.copy2(str(source), str(destination))
        elif operation.operation == 'delete':
            if source.is_dir():
                shutil.rmtree(str(source))
            else:
                source.unlink()
        
        return {"message": f"{operation.operation} completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SCRAPER ROUTES ====================

@api_router.post("/scraper/analyze")
async def analyze_url(task: ScraperTask):
    """Analyze a URL for downloadable media"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(task.url, download=False)
            
            if info:
                result = {
                    "title": info.get('title', 'Unknown'),
                    "url": task.url,
                    "extractor": info.get('extractor', 'unknown'),
                    "duration": info.get('duration'),
                    "thumbnail": info.get('thumbnail'),
                    "formats": [],
                    "entries": []
                }
                
                # Get available formats
                if 'formats' in info:
                    for fmt in info['formats'][:10]:  # Limit formats
                        result['formats'].append({
                            "format_id": fmt.get('format_id'),
                            "ext": fmt.get('ext'),
                            "resolution": fmt.get('resolution'),
                            "filesize": fmt.get('filesize')
                        })
                
                # Get playlist entries if any
                if 'entries' in info:
                    for entry in list(info['entries'])[:50]:  # Limit entries
                        if entry:
                            result['entries'].append({
                                "id": entry.get('id'),
                                "title": entry.get('title'),
                                "url": entry.get('url') or entry.get('webpage_url'),
                                "thumbnail": entry.get('thumbnail'),
                                "duration": entry.get('duration')
                            })
                
                return result
            
            return {"error": "Could not extract info"}
    except Exception as e:
        logger.error(f"Scraper analyze error: {e}")
        return {"error": str(e)}

@api_router.post("/scraper/download")
async def start_download(task: ScraperTask, background_tasks: BackgroundTasks, payload: dict = Depends(verify_token)):
    """Start a download task"""
    task_id = str(uuid.uuid4())
    output_path = task.output_path or str(MEDIA_BASE_PATH / "downloads")
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO scraper_tasks (id, url, status, output_path)
            VALUES (%s, %s, 'pending', %s)
        """, (task_id, task.url, output_path))
        conn.commit()
        
        background_tasks.add_task(run_download, task_id, task.url, output_path)
        
        return {"task_id": task_id, "status": "started"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

async def run_download(task_id: str, url: str, output_path: str):
    """Background download task"""
    conn = None
    cursor = None
    try:
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        ydl_opts = {
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'format': 'best',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([url])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE scraper_tasks 
            SET status = 'completed', completed_at = NOW(), result = %s
            WHERE id = %s
        """, (json.dumps({"download_result": result}), task_id))
        conn.commit()
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scraper_tasks 
                SET status = 'failed', error = %s
                WHERE id = %s
            """, (str(e), task_id))
            conn.commit()
        except:
            pass
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@api_router.get("/scraper/tasks")
async def get_scraper_tasks(limit: int = 20, payload: dict = Depends(verify_token)):
    """Get scraper task history"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM scraper_tasks
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        tasks = cursor.fetchall()
        for task in tasks:
            task['created_at'] = task['created_at'].isoformat() if task['created_at'] else None
            task['completed_at'] = task['completed_at'].isoformat() if task['completed_at'] else None
        
        return {"tasks": tasks}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ==================== CLI ROUTES ====================

@api_router.post("/cli/execute")
async def execute_command(cmd: CLICommand, payload: dict = Depends(verify_token)):
    """Execute a CLI command on the server"""
    # Basic security - block dangerous commands
    blocked_commands = ['rm -rf /', 'mkfs', 'dd if=/dev/zero', ':(){:|:&};:']
    if any(blocked in cmd.command for blocked in blocked_commands):
        raise HTTPException(status_code=403, detail="Command blocked for security")
    
    try:
        process = await asyncio.create_subprocess_shell(
            cmd.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cmd.cwd
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
        
        return {
            "stdout": stdout.decode('utf-8', errors='replace'),
            "stderr": stderr.decode('utf-8', errors='replace'),
            "returncode": process.returncode
        }
    except asyncio.TimeoutError:
        return {"error": "Command timed out", "returncode": -1}
    except Exception as e:
        return {"error": str(e), "returncode": -1}

@api_router.post("/cli/ofscraper")
async def run_ofscraper(params: Dict[str, Any], background_tasks: BackgroundTasks, payload: dict = Depends(verify_token)):
    """Run OFScraper with specified parameters"""
    # Build ofscraper command
    cmd_parts = ["python", "-m", "ofscraper"]
    
    if params.get('posts'):
        cmd_parts.extend(['--posts', params['posts']])
    if params.get('usernames'):
        cmd_parts.extend(['--usernames', params['usernames']])
    if params.get('scrape_paid'):
        cmd_parts.append('--scrape-paid')
    if params.get('scrape_labels'):
        cmd_parts.append('--scrape-labels')
    
    command = ' '.join(cmd_parts)
    
    task_id = str(uuid.uuid4())
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scraper_tasks (id, url, status, output_path)
            VALUES (%s, %s, 'running', %s)
        """, (task_id, f"ofscraper: {command}", str(MEDIA_BASE_PATH)))
        conn.commit()
        
        background_tasks.add_task(run_ofscraper_task, task_id, command)
        
        return {"task_id": task_id, "command": command, "status": "started"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

async def run_ofscraper_task(task_id: str, command: str):
    """Background task to run ofscraper"""
    conn = None
    cursor = None
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE scraper_tasks 
            SET status = %s, completed_at = NOW(), result = %s, error = %s
            WHERE id = %s
        """, (
            'completed' if process.returncode == 0 else 'failed',
            stdout.decode('utf-8', errors='replace')[:10000],
            stderr.decode('utf-8', errors='replace')[:10000],
            task_id
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"OFScraper error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ==================== SYSTEM ROUTES ====================

@api_router.get("/system/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        # Disk usage
        disk_stats = {}
        for mount in ['/mnt/sata_m2', '/mnt/bigdisk']:
            try:
                usage = shutil.disk_usage(mount)
                disk_stats[mount] = {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": round((usage.used / usage.total) * 100, 2)
                }
            except:
                disk_stats[mount] = {"error": "Not accessible"}
        
        return {
            "disk": disk_stats,
            "media_base_path": str(MEDIA_BASE_PATH),
            "legacy_path": str(LEGACY_MEDIA_PATH)
        }
    except Exception as e:
        return {"error": str(e)}

@api_router.get("/")
async def root():
    return {"message": "Clone App API", "version": "1.0.0"}

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Clone App API...")
    try:
        init_database()
    except Exception as e:
        logger.error(f"Startup error: {e}")

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
