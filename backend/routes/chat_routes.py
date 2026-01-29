from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import logging
from database import get_db_connection
from chatgpt_service import chatgpt_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])

# Pydantic Models
class ConversationCreate(BaseModel):
    title: str = "New chat"

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str

class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse

class RegenerateRequest(BaseModel):
    message_id: str

# Routes

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations():
    """Get all conversations ordered by most recent"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC"
            )
            conversations = cursor.fetchall()
            cursor.close()
            
            # Convert datetime to string
            for conv in conversations:
                conv['created_at'] = conv['created_at'].isoformat()
                conv['updated_at'] = conv['updated_at'].isoformat()
            
            return conversations
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(conversation: ConversationCreate):
    """Create a new conversation"""
    try:
        conversation_id = str(uuid.uuid4())
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (id, title) VALUES (%s, %s)",
                (conversation_id, conversation.title)
            )
            conn.commit()
            
            # Fetch the created conversation
            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM conversations WHERE id = %s",
                (conversation_id,)
            )
            result = cursor.fetchone()
            cursor.close()
            
            return {
                "id": result[0],
                "title": result[1],
                "created_at": result[2].isoformat(),
                "updated_at": result[3].isoformat()
            }
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation and all its messages"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))
            conn.commit()
            cursor.close()
            
            return {"message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(conversation_id: str):
    """Get all messages for a conversation"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, conversation_id, role, content, created_at FROM messages WHERE conversation_id = %s ORDER BY created_at ASC",
                (conversation_id,)
            )
            messages = cursor.fetchall()
            cursor.close()
            
            # Convert datetime to string
            for msg in messages:
                msg['created_at'] = msg['created_at'].isoformat()
            
            return messages
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(conversation_id: str, message: MessageCreate):
    """Send a message and get AI response"""
    try:
        # First, check if conversation exists
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, title FROM conversations WHERE id = %s", (conversation_id,))
            conversation = cursor.fetchone()
            
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            # Get conversation history
            cursor.execute(
                "SELECT role, content FROM messages WHERE conversation_id = %s ORDER BY created_at ASC",
                (conversation_id,)
            )
            history = cursor.fetchall()
            
            # Create user message
            user_message_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO messages (id, conversation_id, role, content) VALUES (%s, %s, %s, %s)",
                (user_message_id, conversation_id, "user", message.content)
            )
            conn.commit()
            
            # Fetch created user message
            cursor.execute(
                "SELECT id, conversation_id, role, content, created_at FROM messages WHERE id = %s",
                (user_message_id,)
            )
            user_msg = cursor.fetchone()
            
            # Prepare messages for AI
            ai_messages = []
            for msg in history:
                ai_messages.append({"role": msg["role"], "content": msg["content"]})
            ai_messages.append({"role": "user", "content": message.content})
            
            # Generate AI response
            ai_response = await chatgpt_service.generate_response(ai_messages)
            
            # Save assistant message
            assistant_message_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO messages (id, conversation_id, role, content) VALUES (%s, %s, %s, %s)",
                (assistant_message_id, conversation_id, "assistant", ai_response)
            )
            
            # Update conversation title if it's the first message
            if conversation["title"] == "New chat" and len(history) == 0:
                new_title = await chatgpt_service.generate_title(message.content)
                cursor.execute(
                    "UPDATE conversations SET title = %s WHERE id = %s",
                    (new_title, conversation_id)
                )
            
            # Update conversation updated_at
            cursor.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (conversation_id,)
            )
            
            conn.commit()
            
            # Fetch created assistant message
            cursor.execute(
                "SELECT id, conversation_id, role, content, created_at FROM messages WHERE id = %s",
                (assistant_message_id,)
            )
            assistant_msg = cursor.fetchone()
            
            cursor.close()
            
            return {
                "user_message": {
                    "id": user_msg["id"],
                    "conversation_id": user_msg["conversation_id"],
                    "role": user_msg["role"],
                    "content": user_msg["content"],
                    "created_at": user_msg["created_at"].isoformat()
                },
                "assistant_message": {
                    "id": assistant_msg["id"],
                    "conversation_id": assistant_msg["conversation_id"],
                    "role": assistant_msg["role"],
                    "content": assistant_msg["content"],
                    "created_at": assistant_msg["created_at"].isoformat()
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversations/{conversation_id}/regenerate", response_model=MessageResponse)
async def regenerate_response(conversation_id: str, request: RegenerateRequest):
    """Regenerate the last AI response"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get the message to regenerate
            cursor.execute(
                "SELECT id, role FROM messages WHERE id = %s AND conversation_id = %s",
                (request.message_id, conversation_id)
            )
            message = cursor.fetchone()
            
            if not message or message["role"] != "assistant":
                raise HTTPException(status_code=400, detail="Invalid message for regeneration")
            
            # Delete the old assistant message
            cursor.execute("DELETE FROM messages WHERE id = %s", (request.message_id,))
            conn.commit()
            
            # Get conversation history (excluding the deleted message)
            cursor.execute(
                "SELECT role, content FROM messages WHERE conversation_id = %s ORDER BY created_at ASC",
                (conversation_id,)
            )
            history = cursor.fetchall()
            
            # Prepare messages for AI
            ai_messages = []
            for msg in history:
                ai_messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Generate new AI response
            ai_response = await chatgpt_service.generate_response(ai_messages)
            
            # Save new assistant message
            new_message_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO messages (id, conversation_id, role, content) VALUES (%s, %s, %s, %s)",
                (new_message_id, conversation_id, "assistant", ai_response)
            )
            conn.commit()
            
            # Fetch the new message
            cursor.execute(
                "SELECT id, conversation_id, role, content, created_at FROM messages WHERE id = %s",
                (new_message_id,)
            )
            new_msg = cursor.fetchone()
            cursor.close()
            
            return {
                "id": new_msg["id"],
                "conversation_id": new_msg["conversation_id"],
                "role": new_msg["role"],
                "content": new_msg["content"],
                "created_at": new_msg["created_at"].isoformat()
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
