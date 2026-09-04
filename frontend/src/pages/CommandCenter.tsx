import React, { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';
import ActionCard, { type Action } from '../components/ActionCard';
import { Send, Loader2, Bot, User, Plus, MessageSquare, MoreVertical, Edit2, Trash2, Check, X } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';

interface Chat {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  actions?: Action[];
  metadata?: any;
}

export default function CommandCenter() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Edit State
  const [editingChatId, setEditingChatId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchChats();
  }, []);

  const fetchChats = async () => {
    try {
      const res = await api.get('/chats');
      setChats(res.data);
      if (res.data.length > 0 && !currentChatId) {
        selectChat(res.data[0].id);
      } else if (res.data.length === 0) {
        handleNewChat();
      }
    } catch (err) {
      console.error('Failed to fetch chats', err);
    }
  };

  const selectChat = async (chatId: string) => {
    setCurrentChatId(chatId);
    setMessages([]);
    try {
      const res = await api.get(`/chats/${chatId}`);
      if (res.data.messages.length === 0) {
        setMessages([
          {
            id: '1',
            role: 'assistant',
            content: 'Hello! I am your AI Operations Assistant. What would you like to do today?'
          }
        ]);
      } else {
        setMessages(res.data.messages);
      }
    } catch (err) {
      console.error('Failed to load chat', err);
    }
  };

  const handleNewChat = async () => {
    try {
      const res = await api.post('/chats', { title: 'New Chat' });
      setChats([res.data, ...chats]);
      setCurrentChatId(res.data.id);
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: 'Hello! I am your AI Operations Assistant. What would you like to do today?'
        }
      ]);
    } catch (err) {
      console.error('Failed to create chat', err);
    }
  };

  const handleRenameChat = async (chatId: string) => {
    if (!editTitle.trim()) {
      setEditingChatId(null);
      return;
    }
    try {
      const res = await api.patch(`/chats/${chatId}`, { title: editTitle });
      setChats(chats.map(c => c.id === chatId ? res.data : c));
      setEditingChatId(null);
    } catch (err) {
      console.error('Failed to rename chat', err);
    }
  };

  const handleDeleteChat = async (chatId: string) => {
    try {
      await api.delete(`/chats/${chatId}`);
      setChats(chats.filter(c => c.id !== chatId));
      if (currentChatId === chatId) {
        setCurrentChatId(null);
        setMessages([]);
        if (chats.length > 1) {
          const nextChat = chats.find(c => c.id !== chatId);
          if (nextChat) selectChat(nextChat.id);
        } else {
          handleNewChat();
        }
      }
    } catch (err) {
      console.error('Failed to delete chat', err);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading || !currentChatId) return;

    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post(`/chats/${currentChatId}/messages`, {
        content: userMessage.content
      });

      const assistantMessage: Message = {
        id: response.data.id,
        role: 'assistant',
        content: response.data.content,
        metadata: response.data.metadata
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message || 'Something went wrong.'}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] p-4 sm:p-6 lg:p-8 gap-6">
      
      {/* Sidebar - Chat History */}
      <div className="w-64 flex flex-col bg-white rounded-xl shadow-sm ring-1 ring-gray-200 overflow-hidden shrink-0 hidden md:flex">
        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
          <h2 className="font-semibold text-gray-700 text-sm">Chat History</h2>
          <button 
            onClick={handleNewChat}
            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
            title="New Chat"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {chats.map(chat => (
            <div 
              key={chat.id}
              className={`group flex items-center justify-between p-2.5 rounded-lg cursor-pointer transition-colors ${
                currentChatId === chat.id ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-50 text-gray-600'
              }`}
            >
              <div 
                className="flex items-center gap-3 overflow-hidden flex-1"
                onClick={() => selectChat(chat.id)}
              >
                <MessageSquare className={`w-4 h-4 shrink-0 ${currentChatId === chat.id ? 'text-blue-600' : 'text-gray-400'}`} />
                {editingChatId === chat.id ? (
                  <input
                    autoFocus
                    className="flex-1 text-sm bg-white border border-blue-300 rounded px-1 py-0.5 outline-none"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleRenameChat(chat.id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                ) : (
                  <span className="text-sm truncate pr-2 font-medium">{chat.title}</span>
                )}
              </div>
              
              {/* Actions */}
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                {editingChatId === chat.id ? (
                  <>
                    <button onClick={(e) => { e.stopPropagation(); handleRenameChat(chat.id); }} className="p-1 text-green-600 hover:bg-green-100 rounded">
                      <Check className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={(e) => { e.stopPropagation(); setEditingChatId(null); }} className="p-1 text-gray-500 hover:bg-gray-200 rounded">
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </>
                ) : (
                  <>
                    <button 
                      onClick={(e) => { e.stopPropagation(); setEditTitle(chat.title); setEditingChatId(chat.id); }} 
                      className="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-100 rounded"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button 
                      onClick={(e) => { e.stopPropagation(); handleDeleteChat(chat.id); }} 
                      className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-100 rounded"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-white rounded-xl shadow-sm ring-1 ring-gray-200 overflow-hidden">
        
        {/* Header */}
        <div className="p-4 border-b border-gray-100 bg-white flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-gray-900">
              {chats.find(c => c.id === currentChatId)?.title || "AI Command Center"}
            </h1>
            <p className="mt-0.5 text-xs text-gray-500">
              Chat with your intelligent agents to orchestrate operations.
            </p>
          </div>
          {currentChatId && (
            <div className="text-xs font-medium px-2.5 py-1 bg-green-100 text-green-800 rounded-full flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
              Secure Session
            </div>
          )}
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.map((message) => (
            <div key={message.id} className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 mt-1">
                  <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <Bot className="h-5 w-5 text-blue-600" />
                  </div>
                </div>
              )}
              
              <div className={`flex flex-col gap-2 max-w-[80%] ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`rounded-2xl px-4 py-3 ${
                  message.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-br-none' 
                    : 'bg-gray-100 text-gray-900 rounded-bl-none'
                }`}>
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
                </div>
                
                {/* Render Metadata if agent info exists */}
                {message.metadata?.agent && (
                  <span className="text-[10px] uppercase font-bold text-gray-400 px-1">
                    Served by: {message.metadata.agent}
                  </span>
                )}
              </div>

              {message.role === 'user' && (
                <div className="flex-shrink-0 mt-1">
                  <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
                    <User className="h-5 w-5 text-gray-600" />
                  </div>
                </div>
              )}

            </div>
          ))}
          
          {loading && (
            <div className="flex gap-4 justify-start">
              <div className="flex-shrink-0 mt-1">
                <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
                </div>
              </div>
              <div className="bg-gray-100 rounded-2xl rounded-bl-none px-4 py-3 text-gray-500 text-sm flex items-center gap-2">
                Thinking <span className="animate-pulse">...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white p-4">
          <div className="relative flex items-end gap-2 max-w-4xl mx-auto">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Message your AI..."
              className="flex-1 max-h-32 min-h-[44px] w-full resize-none rounded-xl border border-gray-300 bg-white px-4 py-3 pl-4 pr-12 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-sm"
              rows={1}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading || !currentChatId}
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg p-2 text-blue-600 hover:bg-blue-50 disabled:text-gray-400 disabled:hover:bg-transparent transition-colors"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
          <div className="text-center mt-2">
            <p className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Stateful Database Session Active</p>
          </div>
        </div>
      </div>
    </div>
  );
}
