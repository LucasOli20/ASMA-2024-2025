import React, { useRef, useEffect } from 'react';
import MessageList from './MessageList';
import InputArea from './InputArea';
import { useChat } from '../contexts/ChatContext';
import { Brain, Sparkles, Zap } from 'lucide-react';

const ChatInterface: React.FC = () => {
  const { messages, loading } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="bg-indigo-50 p-6 rounded-full mb-6">
              <Brain className="h-12 w-12 text-indigo-600" strokeWidth={1.5} />
            </div>
            <h2 className="text-xl font-medium text-gray-800 mb-2">
              Olá, como posso ajudar?
            </h2>
            <p className="text-gray-500 max-w-md">
              Envie uma mensagem ou pressione o botão do microfone para começar uma conversa.
            </p>
          </div>
        ) : (
          <>
            <MessageList messages={messages} />
            {loading && (
              <div className="flex items-center justify-center py-8">
                <div className="relative bg-white rounded-2xl shadow-lg p-6 animate-fadeIn">
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-indigo-600 text-white px-4 py-1 rounded-full text-sm font-medium whitespace-nowrap flex items-center gap-2">
                    <Zap className="h-4 w-4" />
                    A raciocinar
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="relative">
                      <div className="absolute inset-0 bg-indigo-500 rounded-full animate-ping opacity-20" />
                      <Brain className="h-8 w-8 text-indigo-600 animate-pulse" />
                    </div>
                    <div className="flex gap-2">
                      {[...Array(3)].map((_, i) => (
                        <div
                          key={i}
                          className="w-3 h-3 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full animate-bounce"
                          style={{ 
                            animationDelay: `${i * 150}ms`,
                            animationDuration: '1s'
                          }}
                        />
                      ))}
                    </div>
                    <Sparkles className="h-6 w-6 text-amber-500 animate-pulse" />
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>
      <InputArea loading={loading} />
    </div>
  );
};

export default ChatInterface;