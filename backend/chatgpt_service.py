from openai import OpenAI
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

class ChatGPTService:
    def __init__(self, model="gpt-4.1"):
        self.model = model
        self.system_prompt = "You are a helpful assistant."
    
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate AI response using OpenAI API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
        
        Returns:
            AI generated response text
        """
        try:
            # Prepare messages for OpenAI API
            api_messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add conversation history
            for msg in messages:
                api_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract response text
            ai_response = response.choices[0].message.content
            logger.info(f"Generated response using {self.model}")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise Exception(f"Failed to generate AI response: {str(e)}")
    
    async def generate_title(self, first_message: str) -> str:
        """
        Generate a conversation title from the first message
        
        Args:
            first_message: First user message in the conversation
        
        Returns:
            Generated title (max 50 chars)
        """
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Generate a short title (max 5 words) for a conversation that starts with the following message. Only return the title, nothing else."},
                    {"role": "user", "content": first_message}
                ],
                temperature=0.7,
                max_tokens=20
            )
            
            title = response.choices[0].message.content.strip()
            # Truncate if too long
            if len(title) > 50:
                title = title[:47] + "..."
            
            return title
            
        except Exception as e:
            logger.error(f"Error generating title: {str(e)}")
            # Fallback to truncated first message
            return first_message[:50] + ("..." if len(first_message) > 50 else "")

# Create singleton instance
chatgpt_service = ChatGPTService()
