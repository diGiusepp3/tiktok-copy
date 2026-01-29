import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import { conversationAPI } from './api/chatApi';
import { toast } from './hooks/use-toast';

const ChatApp = () => {
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load conversations from API
  const loadConversations = async () => {
    try {
      const data = await conversationAPI.getAll();
      setConversations(data);
      
      // Set first conversation as active if exists
      if (data.length > 0) {
        setActiveConversation(data[0]);
        await loadMessages(data[0].id);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
      toast({
        title: 'Error',
        description: 'Failed to load conversations',
        variant: 'destructive'
      });
    }
  };

  // Load messages for a conversation
  const loadMessages = async (conversationId) => {
    try {
      const data = await conversationAPI.getMessages(conversationId);
      setMessages(data);
    } catch (error) {
      console.error('Error loading messages:', error);
      toast({
        title: 'Error',
        description: 'Failed to load messages',
        variant: 'destructive'
      });
    }
  };

  // Handle new chat
  const handleNewChat = async () => {
    try {
      const newConversation = await conversationAPI.create('New chat');
      setConversations([newConversation, ...conversations]);
      setActiveConversation(newConversation);
      setMessages([]);
      
      toast({
        title: 'New chat created',
        description: 'Start a new conversation'
      });
    } catch (error) {
      console.error('Error creating conversation:', error);
      toast({
        title: 'Error',
        description: 'Failed to create new chat',
        variant: 'destructive'
      });
    }
  };

  // Handle conversation selection
  const handleSelectConversation = async (conversation) => {
    setActiveConversation(conversation);
    await loadMessages(conversation.id);
  };

  // Handle delete conversation
  const handleDeleteConversation = async (conversationId) => {
    try {
      await conversationAPI.delete(conversationId);
      
      const updatedConversations = conversations.filter(c => c.id !== conversationId);
      setConversations(updatedConversations);
      
      if (activeConversation?.id === conversationId) {
        if (updatedConversations.length > 0) {
          setActiveConversation(updatedConversations[0]);
          await loadMessages(updatedConversations[0].id);
        } else {
          setActiveConversation(null);
          setMessages([]);
        }
      }
      
      toast({
        title: 'Conversation deleted',
        description: 'The conversation has been removed'
      });
    } catch (error) {
      console.error('Error deleting conversation:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete conversation',
        variant: 'destructive'
      });
    }
  };

  // Handle send message
  const handleSendMessage = async (content) => {
    let currentConversation = activeConversation;
    
    // Create new conversation if none exists
    if (!currentConversation) {
      try {
        currentConversation = await conversationAPI.create('New chat');
        setConversations([currentConversation, ...conversations]);
        setActiveConversation(currentConversation);
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to create conversation',
          variant: 'destructive'
        });
        return;
      }
    }

    // Add user message to UI immediately for better UX
    const tempUserMessage = {
      id: `temp-${Date.now()}`,
      conversation_id: currentConversation.id,
      role: 'user',
      content,
      created_at: new Date().toISOString()
    };

    setMessages([...messages, tempUserMessage]);
    setIsLoading(true);

    try {
      // Send message and get AI response
      const response = await conversationAPI.sendMessage(currentConversation.id, content);
      
      // Replace temp message with actual messages from backend
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== tempUserMessage.id);
        return [...filtered, response.user_message, response.assistant_message];
      });
      
      // Update conversation in list if title changed
      if (currentConversation.title === 'New chat') {
        await loadConversations();
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Remove temp message on error
      setMessages(messages);
      toast({
        title: 'Error',
        description: 'Failed to send message. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle regenerate
  const handleRegenerate = async (messageId) => {
    if (!activeConversation) return;

    const messageIndex = messages.findIndex(m => m.id === messageId);
    if (messageIndex === -1) return;

    // Remove the assistant message from UI
    const updatedMessages = messages.slice(0, messageIndex);
    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      // Call regenerate API
      const newMessage = await conversationAPI.regenerate(activeConversation.id, messageId);
      
      // Add new response to messages
      setMessages([...updatedMessages, newMessage]);
      
      toast({
        title: 'Response regenerated',
        description: 'A new response has been generated'
      });
    } catch (error) {
      console.error('Error regenerating response:', error);
      // Restore original messages on error
      setMessages(messages);
      toast({
        title: 'Error',
        description: 'Failed to regenerate response. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#343541] text-white overflow-hidden">
      <Sidebar
        conversations={conversations}
        activeConversation={activeConversation}
        onNewChat={handleNewChat}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={handleDeleteConversation}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      <ChatArea
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        onRegenerate={handleRegenerate}
        activeConversation={activeConversation}
        sidebarOpen={sidebarOpen}
      />
    </div>
  );
};

export default ChatApp;