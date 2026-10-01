import React, { useState } from 'react';
import { MessageSquare, X, Send, Bot, Sparkles, ShieldCheck } from 'lucide-react';
import api from '../services/api';

interface Message {
  sender: 'user' | 'bot';
  text: string;
  timestamp: string;
}

interface ChatbotDrawerProps {
  pageContext?: string;
}

const ChatbotDrawer: React.FC<ChatbotDrawerProps> = ({ pageContext = 'dashboard' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'bot',
      text: `Hi! I'm RansomGuard Copilot. How can I assist your security operations today?`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const quickPrompts = [
    'Set up my first endpoint',
    'Run a safe simulation',
    'Understand the AI',
    'Investigate an alert',
    'Configure the dashboard'
  ];

  const handleSend = async (questionText?: string) => {
    const query = questionText || input;
    if (!query.trim()) return;

    const userMsg: Message = {
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!questionText) setInput('');
    setLoading(true);

    try {
      const res = await api.post('/chatbot/query', {
        question: query,
        page_context: pageContext
      });

      const botMsg: Message = {
        sender: 'bot',
        text: res.data.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: "I don't have enough system data to confirm that at this moment.",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Need Help Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-3 rounded-full shadow-lg flex items-center space-x-2 border border-blue-400/30 transition-transform transform hover:scale-105"
      >
        <Bot className="h-5 w-5" />
        <span className="text-sm">RansomGuard Copilot</span>
      </button>

      {/* Slide-out Drawer */}
      {isOpen && (
        <div className="fixed inset-y-0 right-0 w-96 bg-[#0E1526] border-l border-gray-800 shadow-2xl z-50 flex flex-col justify-between">
          {/* Header */}
          <div className="p-4 border-b border-gray-800 flex items-center justify-between bg-[#0A0E17]">
            <div className="flex items-center space-x-2">
              <div className="p-1.5 bg-blue-950 border border-blue-800 rounded-lg text-blue-400">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-semibold text-sm text-gray-200">RansomGuard Copilot</h3>
                <span className="text-[10px] text-emerald-400 flex items-center gap-1 font-mono">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                  Active Context: {pageContext}
                </span>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-gray-800"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Messages List */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[85%] px-3.5 py-2.5 rounded-2xl text-xs leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-blue-600 text-white rounded-br-none'
                      : 'bg-gray-800 text-gray-200 border border-gray-700/60 rounded-bl-none'
                  }`}
                >
                  {msg.text}
                </div>
                <span className="text-[10px] text-gray-500 mt-1 font-mono">{msg.timestamp}</span>
              </div>
            ))}
            {loading && (
              <div className="text-xs text-blue-400 animate-pulse font-mono flex items-center space-x-1">
                <span>Analyzing telemetry & model state...</span>
              </div>
            )}
          </div>

          {/* Quick Action Chips */}
          <div className="p-3 border-t border-gray-800/60 bg-[#0A0E17]/60 overflow-x-auto flex gap-1.5 text-nowrap">
            {quickPrompts.map((prompt, i) => (
              <button
                key={i}
                onClick={() => handleSend(prompt)}
                className="px-2.5 py-1 text-[11px] bg-gray-800/80 hover:bg-gray-700 text-blue-300 rounded-full border border-gray-700 transition"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <div className="p-3 border-t border-gray-800 bg-[#0A0E17]">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center space-x-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about setup, AI, or incidents..."
                className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-xs text-gray-200 focus:outline-none focus:border-blue-500"
              />
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-500 text-white p-2 rounded-lg transition disabled:opacity-50"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatbotDrawer;
