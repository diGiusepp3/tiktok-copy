# ChatGPT Clone - Backend Integration Contracts

## Database Schema (MySQL)

### Table: conversations
```sql
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Table: messages
```sql
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36) NOT NULL,
    role ENUM('user', 'assistant') NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);
```

## API Endpoints

### 1. GET /api/conversations
- **Purpose**: Fetch all conversations
- **Response**: List of conversation objects

### 2. POST /api/conversations
- **Purpose**: Create new conversation
- **Body**: `{ "title": string }`
- **Response**: New conversation object

### 3. DELETE /api/conversations/{conversation_id}
- **Purpose**: Delete a conversation and its messages
- **Response**: Success message

### 4. GET /api/conversations/{conversation_id}/messages
- **Purpose**: Get all messages for a conversation
- **Response**: List of message objects

### 5. POST /api/conversations/{conversation_id}/messages
- **Purpose**: Send user message and get AI response
- **Body**: `{ "content": string }`
- **Response**: Both user and assistant messages

### 6. POST /api/conversations/{conversation_id}/regenerate
- **Purpose**: Regenerate last AI response
- **Body**: `{ "message_id": string }`
- **Response**: New assistant message

## Mock Data to Replace

### Frontend: /app/frontend/src/data/mockData.js
- Remove `mockConversations`, `mockMessages`, `generateMockResponse`
- Replace with actual API calls using axios

### Frontend: /app/frontend/src/ChatApp.jsx
- Replace all mock data loading with API calls
- Implement real-time message streaming (optional)

## OpenAI Integration

- **Model**: gpt-4.1
- **API Key**: sk-proj-UkGGLNXO... (stored in .env)
- **System Prompt**: "You are a helpful assistant."
- **Temperature**: 0.7
- **Max Tokens**: 2000

## MySQL Connection

- **Host**: mgielen.zapto.org
- **Port**: 3306
- **User**: matthias
- **Password**: DigiuSeppe2018___
- **Database**: Create new database "chatgpt_clone"

## Frontend-Backend Integration

1. Replace mock conversation loading with GET /api/conversations
2. Replace mock message loading with GET /api/conversations/{id}/messages
3. Replace generateMockResponse with POST /api/conversations/{id}/messages
4. Add proper error handling and loading states
5. Keep UI/UX exactly the same
