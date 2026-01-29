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
  const handleDeleteConversation = (conversationId) => {
    const updatedConversations = conversations.filter(c => c.id !== conversationId);
    setConversations(updatedConversations);
    
    if (activeConversation?.id === conversationId) {
      if (updatedConversations.length > 0) {
        setActiveConversation(updatedConversations[0]);
        setMessages(mockMessages[updatedConversations[0].id] || []);
      } else {
        setActiveConversation(null);
        setMessages([]);
      }
    }
    
    toast({
      title: 'Conversation deleted',
      description: 'The conversation has been removed'
    });
  };

  // Handle send message
  const handleSendMessage = async (content) => {
    if (!activeConversation) {
      // Create new conversation if none exists
      const newConversation = {
        id: `new-${Date.now()}`,
        title: content.slice(0, 30) + (content.length > 30 ? '...' : ''),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      setConversations([newConversation, ...conversations]);
      setActiveConversation(newConversation);
    }

    // Add user message
    const userMessage = {
      id: `msg-${Date.now()}`,
      conversation_id: activeConversation?.id,
      role: 'user',
      content,
      created_at: new Date().toISOString()
    };

    setMessages([...messages, userMessage]);
    setIsLoading(true);

    try {
      // Generate mock AI response
      const aiResponse = await generateMockResponse(content);
      
      const assistantMessage = {
        id: `msg-${Date.now()}-ai`,
        conversation_id: activeConversation?.id,
        role: 'assistant',
        content: aiResponse,
        created_at: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Update conversation title if it's a new chat
      if (activeConversation && activeConversation.title === 'New chat') {
        const updatedConversation = {
          ...activeConversation,
          title: content.slice(0, 30) + (content.length > 30 ? '...' : ''),
          updated_at: new Date().toISOString()
        };
        setActiveConversation(updatedConversation);
        setConversations(conversations.map(c => 
          c.id === activeConversation.id ? updatedConversation : c
        ));
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to get response. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle regenerate
  const handleRegenerate = async (messageId) => {
    const messageIndex = messages.findIndex(m => m.id === messageId);
    if (messageIndex === -1) return;

    // Get the previous user message
    const userMessage = messages[messageIndex - 1];
    if (!userMessage || userMessage.role !== 'user') return;

    // Remove the assistant message
    const updatedMessages = messages.slice(0, messageIndex);
    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      // Generate new mock response
      const aiResponse = await generateMockResponse(userMessage.content);
      
      const assistantMessage = {
        id: `msg-${Date.now()}-regen`,
        conversation_id: activeConversation?.id,
        role: 'assistant',
        content: aiResponse,
        created_at: new Date().toISOString()
      };

      setMessages([...updatedMessages, assistantMessage]);
      
      toast({
        title: 'Response regenerated',
        description: 'A new response has been generated'
      });
    } catch (error) {
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