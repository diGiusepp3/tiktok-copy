import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, Trash2, Menu, Plus, Settings } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { ScrollArea } from '../components/ui/scroll-area';
import { Avatar, AvatarFallback } from '../components/ui/avatar';

// This is a placeholder chat - can be connected to an AI API later
export default function ChatAssistant() {
  const [messages, setMessages] = useState([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your Clone assistant. I can help you with:\n\n• Managing your media files\n• Understanding scraper settings\n• Navigating the app\n• General questions\n\nHow can I help you today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Simulate AI response (placeholder)
    setTimeout(() => {
      const responses = [
        'I understand you\'re asking about that. Let me help you with some guidance.',
        'Great question! Here\'s what I can tell you about that topic.',
        'I\'d be happy to assist with that. Here\'s some information that might help.',
        'That\'s an interesting query. Based on your question, I\'d suggest the following approach.'
      ];
      
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responses[Math.floor(Math.random() * responses.length)] + '\n\nNote: This is a placeholder response. Connect an AI API for real functionality.'
      };

      setMessages(prev => [...prev, assistantMessage]);
      setLoading(false);
    }, 1000);
  };

  const clearChat = () => {
    setMessages([{
      id: Date.now().toString(),
      role: 'assistant',
      content: 'Chat cleared. How can I help you?'
    }]);
  };

  return (
    <div className="min-h-screen bg-[#050505] flex" data-testid="chat-assistant-page">
      {/* Sidebar */}
      <AnimatePresence>
        {showSidebar && (
          <motion.div
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            className="fixed inset-y-0 left-0 w-72 bg-[#0a0a0a] border-r border-[#222] z-50 flex flex-col"
          >
            <div className="p-4 border-b border-[#222]">
              <Button 
                className="w-full bg-[#1a1a1a] hover:bg-[#252525] text-white justify-start gap-2"
                data-testid="new-chat-button"
              >
                <Plus className="w-4 h-4" />
                New Chat
              </Button>
            </div>
            
            <ScrollArea className="flex-1 p-2">
              <div className="space-y-1">
                <div className="px-3 py-2 text-xs text-gray-500 uppercase">Today</div>
                <button className="w-full text-left px-3 py-2 rounded-lg bg-[#1a1a1a] text-white text-sm truncate">
                  Current conversation
                </button>
              </div>
            </ScrollArea>
            
            <div className="p-4 border-t border-[#222]">
              <Button 
                variant="ghost" 
                className="w-full justify-start text-gray-400 hover:text-white"
                onClick={() => setShowSidebar(false)}
              >
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Overlay */}
      {showSidebar && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setShowSidebar(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="sticky top-0 z-30 bg-[#050505]/90 backdrop-blur-lg border-b border-[#222] px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSidebar(!showSidebar)}
                className="text-gray-400"
                data-testid="toggle-sidebar"
              >
                <Menu className="w-5 h-5" />
              </Button>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#E91E63] to-[#9C27B0] flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <h1 className="text-lg font-bold text-white">Assistant</h1>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearChat}
              className="text-gray-400 hover:text-white"
              data-testid="clear-chat"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Messages */}
        <ScrollArea ref={scrollRef} className="flex-1 pb-32">
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : ''}`}
                data-testid={`message-${message.id}`}
              >
                {message.role === 'assistant' && (
                  <Avatar className="w-8 h-8 shrink-0">
                    <AvatarFallback className="bg-gradient-to-br from-[#E91E63] to-[#9C27B0]">
                      <Bot className="w-4 h-4 text-white" />
                    </AvatarFallback>
                  </Avatar>
                )}
                
                <div className={`max-w-[80%] ${
                  message.role === 'user' 
                    ? 'bg-[#E91E63] text-white rounded-2xl rounded-br-md px-4 py-3' 
                    : 'bg-[#1a1a1a] text-gray-200 rounded-2xl rounded-bl-md px-4 py-3'
                }`}>
                  <p className="whitespace-pre-wrap text-sm">{message.content}</p>
                </div>
                
                {message.role === 'user' && (
                  <Avatar className="w-8 h-8 shrink-0">
                    <AvatarFallback className="bg-[#00F0FF] text-black">
                      <User className="w-4 h-4" />
                    </AvatarFallback>
                  </Avatar>
                )}
              </motion.div>
            ))}
            
            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-4"
              >
                <Avatar className="w-8 h-8">
                  <AvatarFallback className="bg-gradient-to-br from-[#E91E63] to-[#9C27B0]">
                    <Bot className="w-4 h-4 text-white" />
                  </AvatarFallback>
                </Avatar>
                <div className="bg-[#1a1a1a] rounded-2xl rounded-bl-md px-4 py-3">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </ScrollArea>

        {/* Input */}
        <div className="fixed bottom-20 left-0 right-0 p-4 bg-gradient-to-t from-[#050505] to-transparent">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="flex items-center gap-2 bg-[#1a1a1a] rounded-2xl border border-[#333] focus-within:border-[#E91E63] px-4 py-2">
              <Input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Send a message..."
                className="flex-1 bg-transparent border-none focus:ring-0 text-white placeholder:text-gray-500"
                disabled={loading}
                data-testid="chat-input"
              />
              <Button
                type="submit"
                disabled={loading || !input.trim()}
                className="bg-[#E91E63] hover:bg-[#C2185B] rounded-xl"
                data-testid="send-message"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-center text-xs text-gray-500 mt-2">
              Connect an AI API for intelligent responses
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
