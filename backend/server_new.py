from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI, APIError
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import json
import asyncio
from passlib.context import CryptContext
import jwt
import shutil

# Import database modules
from database_mysql import init_database, get_db_connection

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (for ChatGPT feature)
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# OpenAI client (for ChatGPT feature)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
security = HTTPBearer()

# File storage paths
STORAGE_BASE_PATH = Path("/mnt/bigdisk/images")

# Create the main app
app = FastAPI(title="Adult TikTok API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MySQL database
init_database()

# ============================================================================
# MODELS
# ============================================================================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_admin: bool = False
    is_creator: bool = False
    is_verified: bool = False
    followers_count: int = 0
    following_count: int = 0
    likes_count: int = 0
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile

class PostCreate(BaseModel):
    caption: Optional[str] = None
    subscribers_only: bool = False

class Post(BaseModel):
    id: str
    user_id: str
    username: str
    user_avatar: Optional[str] = None
    is_verified: bool
    type: str
    file_url: str
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = None
    likes_count: int
    comments_count: int
    shares_count: int
    views_count: int
    is_liked: bool = False
    is_following: bool = False
    subscribers_only: bool
    created_at: datetime

class Comment(BaseModel):
    id: str
    user_id: str
    username: str
    user_avatar: Optional[str] = None
    content: str
    likes_count: int
    created_at: datetime

class CommentCreate(BaseModel):
    content: str

# ChatGPT Models (keeping existing functionality)
class ChatSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatSessionCreate(BaseModel):
    title: Optional[str] = "New Chat"

class ChatSessionUpdate(BaseModel):
    title: str

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageCreate(BaseModel):
    content: str

# ============================================================================
# UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=30)
    payload = {
        "sub": user_id,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    user_id = str(uuid.uuid4())
    hashed_pw = hash_password(user_data.password)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, display_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, user_data.username, user_data.email, hashed_pw, user_data.display_name or user_data.username))
            conn.commit()
            cursor.close()
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Fetch created user
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
    
    token = create_access_token(user_id)
    
    return {
        "access_token": token,
        "user": user
    }

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user"""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (credentials.username,))
        user = cursor.fetchone()
        cursor.close()
    
    if not user or not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user['id'])
    
    return {
        "access_token": token,
        "user": user
    }

@api_router.get("/auth/me", response_model=UserProfile)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

# ============================================================================
# POSTS ENDPOINTS
# ============================================================================

@api_router.get("/posts/feed", response_model=List[Post])
async def get_feed(skip: int = 0, limit: int = 20, current_user: Optional[dict] = None):
    """Get posts feed"""
    # For now, get public posts. Later add subscription logic
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                p.*,
                u.username,
                u.avatar_url as user_avatar,
                u.is_verified,
                (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as actual_likes_count
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.is_public = TRUE
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, skip))
        posts = cursor.fetchall()
        cursor.close()
    
    # Convert to response format
    result = []
    for post in posts:
        # Build file URLs
        file_url = f"/api/media/{post['user_id']}/posts/{post['type']}s/{Path(post['file_path']).name}"
        thumbnail_url = None
        if post.get('thumbnail_path'):
            thumbnail_url = f"/api/media/{post['user_id']}/posts/images/{Path(post['thumbnail_path']).name}"
        
        result.append({
            **post,
            'file_url': file_url,
            'thumbnail_url': thumbnail_url,
            'is_liked': False,  # TODO: Check if current user liked
            'is_following': False  # TODO: Check if current user follows
        })
    
    return result

@api_router.post("/posts/upload")
async def upload_post(
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    subscribers_only: bool = Form(False),
    current_user: dict = Depends(get_current_user)
):
    """Upload a new post (image or video)"""
    # Determine file type
    content_type = file.content_type
    if content_type.startswith('image/'):
        post_type = 'image'
        subfolder = 'images'
    elif content_type.startswith('video/'):
        post_type = 'video'
        subfolder = 'videos'
    else:
        raise HTTPException(status_code=400, detail="Only images and videos are supported")
    
    # Create user directory structure
    user_dir = STORAGE_BASE_PATH / current_user['username'] / 'posts' / subfolder
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_extension = Path(file.filename).suffix
    file_name = f"{uuid.uuid4()}{file_extension}"
    file_path = user_dir / file_name
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create post in database
    post_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO posts (id, user_id, type, file_path, caption, subscribers_only)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (post_id, current_user['id'], post_type, str(file_path), caption, subscribers_only))
        conn.commit()
        cursor.close()
    
    return {"message": "Post uploaded successfully", "post_id": post_id}

@api_router.post("/posts/{post_id}/like")
async def like_post(post_id: str, current_user: dict = Depends(get_current_user)):
    """Like/unlike a post"""
    like_id = str(uuid.uuid4())
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Check if already liked
            cursor.execute("SELECT id FROM likes WHERE user_id = %s AND post_id = %s", 
                         (current_user['id'], post_id))
            existing = cursor.fetchone()
            
            if existing:
                # Unlike
                cursor.execute("DELETE FROM likes WHERE user_id = %s AND post_id = %s",
                             (current_user['id'], post_id))
                cursor.execute("UPDATE posts SET likes_count = likes_count - 1 WHERE id = %s", (post_id,))
                action = "unliked"
            else:
                # Like
                cursor.execute("INSERT INTO likes (id, user_id, post_id) VALUES (%s, %s, %s)",
                             (like_id, current_user['id'], post_id))
                cursor.execute("UPDATE posts SET likes_count = likes_count + 1 WHERE id = %s", (post_id,))
                action = "liked"
            
            conn.commit()
            cursor.close()
        
        return {"message": f"Post {action}", "action": action}
    except Exception as e:
        logger.error(f"Like error: {e}")
        raise HTTPException(status_code=500, detail="Failed to like post")

@api_router.get("/posts/{post_id}/comments", response_model=List[Comment])
async def get_comments(post_id: str, skip: int = 0, limit: int = 50):
    """Get comments for a post"""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                c.*,
                u.username,
                u.avatar_url as user_avatar
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
        """, (post_id, limit, skip))
        comments = cursor.fetchall()
        cursor.close()
    
    return comments

@api_router.post("/posts/{post_id}/comments")
async def add_comment(
    post_id: str, 
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a comment to a post"""
    comment_id = str(uuid.uuid4())
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO comments (id, user_id, post_id, content)
            VALUES (%s, %s, %s, %s)
        """, (comment_id, current_user['id'], post_id, comment_data.content))
        cursor.execute("UPDATE posts SET comments_count = comments_count + 1 WHERE id = %s", (post_id,))
        conn.commit()
        cursor.close()
    
    return {"message": "Comment added", "comment_id": comment_id}

# ============================================================================
# USER ENDPOINTS
# ============================================================================

@api_router.get("/users/{username}", response_model=UserProfile)
async def get_user_profile(username: str):
    """Get user profile by username"""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@api_router.post("/users/{user_id}/follow")
async def follow_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Follow/unfollow a user"""
    if user_id == current_user['id']:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    follow_id = str(uuid.uuid4())
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Check if already following
            cursor.execute("SELECT id FROM follows WHERE follower_id = %s AND following_id = %s",
                         (current_user['id'], user_id))
            existing = cursor.fetchone()
            
            if existing:
                # Unfollow
                cursor.execute("DELETE FROM follows WHERE follower_id = %s AND following_id = %s",
                             (current_user['id'], user_id))
                cursor.execute("UPDATE users SET followers_count = followers_count - 1 WHERE id = %s", (user_id,))
                cursor.execute("UPDATE users SET following_count = following_count - 1 WHERE id = %s", (current_user['id'],))
                action = "unfollowed"
            else:
                # Follow
                cursor.execute("INSERT INTO follows (id, follower_id, following_id) VALUES (%s, %s, %s)",
                             (follow_id, current_user['id'], user_id))
                cursor.execute("UPDATE users SET followers_count = followers_count + 1 WHERE id = %s", (user_id,))
                cursor.execute("UPDATE users SET following_count = following_count + 1 WHERE id = %s", (current_user['id'],))
                action = "followed"
            
            conn.commit()
            cursor.close()
        
        return {"message": f"User {action}", "action": action}
    except Exception as e:
        logger.error(f"Follow error: {e}")
        raise HTTPException(status_code=500, detail="Failed to follow user")

# ============================================================================
# MEDIA SERVING
# ============================================================================

@api_router.get("/media/{username}/{message_type}/{media_type}/{filename}")
async def serve_media(username: str, message_type: str, media_type: str, filename: str):
    """Serve media files"""
    file_path = STORAGE_BASE_PATH / username / message_type / media_type / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)

# ============================================================================
# CHATGPT ENDPOINTS (ADMIN PANEL - keeping existing functionality)
# ============================================================================

@api_router.get("/chatgpt")
async def chatgpt_root():
    return {"message": "Unrestricted AI API - Admin Panel"}

@api_router.post("/chatgpt/sessions", response_model=ChatSession)
async def create_session(input: ChatSessionCreate):
    session = ChatSession(title=input.title or "New Chat")
    doc = session.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.chat_sessions.insert_one(doc)
    return session

@api_router.get("/chatgpt/sessions", response_model=List[ChatSession])
async def get_sessions():
    sessions = await db.chat_sessions.find({}, {"_id": 0}).sort("updated_at", -1).to_list(100)
    for s in sessions:
        if isinstance(s['created_at'], str):
            s['created_at'] = datetime.fromisoformat(s['created_at'])
        if isinstance(s['updated_at'], str):
            s['updated_at'] = datetime.fromisoformat(s['updated_at'])
    return sessions

@api_router.get("/chatgpt/sessions/{session_id}", response_model=ChatSession)
async def get_session(session_id: str):
    session = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if isinstance(session['created_at'], str):
        session['created_at'] = datetime.fromisoformat(session['created_at'])
    if isinstance(session['updated_at'], str):
        session['updated_at'] = datetime.fromisoformat(session['updated_at'])
    return session

@api_router.put("/chatgpt/sessions/{session_id}", response_model=ChatSession)
async def update_session(session_id: str, input: ChatSessionUpdate):
    result = await db.chat_sessions.update_one(
        {"id": session_id},
        {"$set": {"title": input.title, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return await get_session(session_id)

@api_router.delete("/chatgpt/sessions/{session_id}")
async def delete_session(session_id: str):
    await db.chat_sessions.delete_one({"id": session_id})
    await db.messages.delete_many({"session_id": session_id})
    return {"status": "deleted"}

@api_router.get("/chatgpt/sessions/{session_id}/messages", response_model=List[Message])
async def get_messages(session_id: str):
    messages = await db.messages.find({"session_id": session_id}, {"_id": 0}).sort("created_at", 1).to_list(1000)
    for m in messages:
        if isinstance(m['created_at'], str):
            m['created_at'] = datetime.fromisoformat(m['created_at'])
    return messages

@api_router.post("/chatgpt/sessions/{session_id}/messages", response_model=Message)
async def send_message(session_id: str, input: MessageCreate):
    session = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    user_msg = Message(session_id=session_id, role="user", content=input.content)
    user_doc = user_msg.model_dump()
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    await db.messages.insert_one(user_doc)
    
    history = await db.messages.find({"session_id": session_id}, {"_id": 0}).sort("created_at", 1).to_list(100)
    
    try:
        if openai_client is None:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

        messages = []
        for msg in history:
            if msg['role'] in ('user', 'assistant'):
                messages.append({"role": msg['role'], "content": msg['content']})
        messages.append({"role": "user", "content": input.content})

        completion = await openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=512,
            temperature=0.7,
        )

        ai_content = completion.choices[0].message.content if completion.choices else ""

        ai_msg = Message(session_id=session_id, role="assistant", content=ai_content)
        ai_doc = ai_msg.model_dump()
        ai_doc['created_at'] = ai_doc['created_at'].isoformat()
        await db.messages.insert_one(ai_doc)
        
        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if session.get('title') == "New Chat":
            update_data['title'] = input.content[:50] + ("..." if len(input.content) > 50 else "")
        await db.chat_sessions.update_one({"id": session_id}, {"$set": update_data})
        
        return ai_msg
        
    except APIError as e:
        logger.error(f"AI generation error: {e}")
        error_msg = Message(
            session_id=session_id, 
            role="assistant", 
            content=f"Error generating response: {str(e)}"
        )
        error_doc = error_msg.model_dump()
        error_doc['created_at'] = error_doc['created_at'].isoformat()
        await db.messages.insert_one(error_doc)
        return error_msg

@api_router.get("/chatgpt/sessions/{session_id}/export")
async def export_session(session_id: str, format: str = "json"):
    session = await db.chat_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = await db.messages.find({"session_id": session_id}, {"_id": 0}).sort("created_at", 1).to_list(1000)
    
    if format == "txt":
        content = f"# {session.get('title', 'Chat Export')}\n"
        content += f"# Exported: {datetime.now(timezone.utc).isoformat()}\n\n"
        for msg in messages:
            role = "USER" if msg['role'] == 'user' else "AI"
            content += f"[{role}]\n{msg['content']}\n\n"
        return StreamingResponse(
            iter([content]),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=chat_{session_id}.txt"}
        )
    else:
        export_data = {
            "session": {
                "id": session.get('id'),
                "title": session.get('title'),
                "created_at": session.get('created_at'),
                "updated_at": session.get('updated_at')
            },
            "messages": [{"role": m['role'], "content": m['content'], "created_at": m['created_at']} for m in messages],
            "exported_at": datetime.now(timezone.utc).isoformat()
        }
        return StreamingResponse(
            iter([json.dumps(export_data, indent=2)]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=chat_{session_id}.json"}
        )

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
