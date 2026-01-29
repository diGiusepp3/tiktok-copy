import React from 'react';
import { Plus, MessageSquare, Trash2, PanelLeftClose, PanelLeft } from 'lucide-react';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';

const Sidebar = ({ conversations, activeConversation, onNewChat, onSelectConversation, onDeleteConversation, isOpen, onToggle }) => {
  return (
    <>
      {!isOpen && (
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="fixed top-4 left-4 z-50 bg-[#202123] hover:bg-[#2a2b32] text-white"
        >
          <PanelLeft className="h-5 w-5" />
        </Button>
      )}
      
      <div className={`fixed top-0 left-0 h-full bg-[#202123] border-r border-[#4d4d4f] transition-all duration-300 z-40 ${
        isOpen ? 'w-[260px]' : 'w-0 overflow-hidden'
      }`}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-3 border-b border-[#4d4d4f]">
            <Button
              onClick={onNewChat}
              className="flex-1 bg-transparent border border-[#4d4d4f] hover:bg-[#2a2b32] text-white justify-start gap-2"
            >
              <Plus className="h-4 w-4" />
              New chat
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggle}
              className="ml-2 hover:bg-[#2a2b32] text-white"
            >
              <PanelLeftClose className="h-5 w-5" />
            </Button>
          </div>

          {/* Conversations List */}
          <ScrollArea className="flex-1 px-2 py-3">
            <div className="space-y-1">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={`group flex items-center justify-between gap-2 p-3 rounded-lg cursor-pointer transition-colors ${
                    activeConversation?.id === conversation.id
                      ? 'bg-[#343541]'
                      : 'hover:bg-[#2a2b32]'
                  }`}
                  onClick={() => onSelectConversation(conversation)}
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <MessageSquare className="h-4 w-4 text-gray-400 flex-shrink-0" />
                    <span className="text-sm text-gray-100 truncate">
                      {conversation.title}
                    </span>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="opacity-0 group-hover:opacity-100 h-8 w-8 hover:bg-[#4d4d4f] text-gray-400 hover:text-red-400 flex-shrink-0"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteConversation(conversation.id);
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </ScrollArea>

          {/* Footer */}
          <div className="p-3 border-t border-[#4d4d4f]">
            <div className="text-xs text-gray-400 text-center">
              ChatGPT Clone
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;