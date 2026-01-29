import React, { useRef, useEffect } from 'react';
import { Send, RotateCw } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { ScrollArea } from './ui/scroll-area';

const MessageBubble = ({ message, onRegenerate }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`w-full py-6 px-4 ${
      isUser ? 'bg-transparent' : 'bg-[#444654]'
    }`}>
      <div className="max-w-3xl mx-auto flex gap-6">
        <div className={`w-8 h-8 rounded-sm flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-[#5436DA]' : 'bg-[#19c37d]'
        }`}>
          <span className="text-white text-sm font-semibold">
            {isUser ? 'U' : 'AI'}
          </span>
        </div>
        <div className="flex-1 space-y-3">
          <div className="text-gray-100 text-[15px] leading-7 whitespace-pre-wrap">
            {message.content}
          </div>
          {!isUser && message.showRegenerate && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onRegenerate(message.id)}
              className="text-gray-400 hover:text-gray-100 hover:bg-[#2a2b32] gap-2"
            >
              <RotateCw className="h-3 w-3" />
              Regenerate
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

const ChatArea = ({ messages, onSendMessage, isLoading, onRegenerate, activeConversation, sidebarOpen }) => {
  const [inputValue, setInputValue] = React.useState('');
  const scrollRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue);
      setInputValue('');
      textareaRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className={`flex-1 flex flex-col h-screen transition-all duration-300 ${
      sidebarOpen ? 'ml-[260px]' : 'ml-0'
    }`}>
      {/* Messages Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-[#19c37d] mx-auto flex items-center justify-center">
                <span className="text-white text-xl font-semibold">AI</span>
              </div>
              <h2 className="text-2xl text-gray-100 font-medium">How can I help you today?</h2>
            </div>
          </div>
        ) : (
          <div>
            {messages.map((message, index) => (
              <MessageBubble
                key={message.id}
                message={{
                  ...message,
                  showRegenerate: index === messages.length - 1 && message.role === 'assistant'
                }}
                onRegenerate={onRegenerate}
              />
            ))}
            {isLoading && (
              <div className="w-full py-6 px-4 bg-[#444654]">
                <div className="max-w-3xl mx-auto flex gap-6">
                  <div className="w-8 h-8 rounded-sm bg-[#19c37d] flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-sm font-semibold">AI</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-[#4d4d4f] bg-[#343541]">
        <div className="max-w-3xl mx-auto py-6 px-4">
          <form onSubmit={handleSubmit} className="relative">
            <Textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Send a message..."
              className="w-full bg-[#40414f] border-0 text-gray-100 placeholder-gray-400 resize-none pr-12 min-h-[52px] max-h-[200px] focus-visible:ring-0 focus-visible:ring-offset-0"
              rows={1}
              disabled={isLoading}
            />
            <Button
              type="submit"
              size="icon"
              disabled={!inputValue.trim() || isLoading}
              className="absolute right-2 bottom-2 bg-transparent hover:bg-[#2a2b32] disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Send className="h-4 w-4 text-gray-400" />
            </Button>
          </form>
          <div className="text-xs text-gray-500 text-center mt-3">
            ChatGPT can make mistakes. Check important info.
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatArea;