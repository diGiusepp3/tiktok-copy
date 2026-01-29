import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Conversation API
export const conversationAPI = {
  // Get all conversations
  getAll: async () => {
    const response = await axios.get(`${API}/conversations`);
    return response.data;
  },

  // Create new conversation
  create: async (title = 'New chat') => {
    const response = await axios.post(`${API}/conversations`, { title });
    return response.data;
  },

  // Delete conversation
  delete: async (conversationId) => {
    const response = await axios.delete(`${API}/conversations/${conversationId}`);
    return response.data;
  },

  // Get messages for a conversation
  getMessages: async (conversationId) => {
    const response = await axios.get(`${API}/conversations/${conversationId}/messages`);
    return response.data;
  },

  // Send message and get AI response
  sendMessage: async (conversationId, content) => {
    const response = await axios.post(
      `${API}/conversations/${conversationId}/messages`,
      { content }
    );
    return response.data;
  },

  // Regenerate last AI response
  regenerate: async (conversationId, messageId) => {
    const response = await axios.post(
      `${API}/conversations/${conversationId}/regenerate`,
      { message_id: messageId }
    );
    return response.data;
  }
};
