import React from 'react';
import { Brain } from 'lucide-react';
import { useChat } from '../contexts/ChatContext';

const Header: React.FC = () => {
  const { currentSubject } = useChat();

  return (
    <header className="bg-white border-b border-gray-100 shadow-sm py-4">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-r from-indigo-500 to-purple-500 p-2 rounded-lg">
            <Brain className="h-8 w-8 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">MentorAI</h1>
            {currentSubject && (
              <p className="text-sm text-gray-500 capitalize">
                Professor de {currentSubject}
              </p>
            )}
          </div>
        </div>
        
        <div className="hidden sm:flex items-center space-x-4">
          <a href="#" className="text-gray-500 hover:text-gray-700 text-sm">Sobre</a>
          <a href="#" className="text-gray-500 hover:text-gray-700 text-sm">Ajuda</a>
          <button className="bg-indigo-50 text-indigo-600 px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-100 transition-colors duration-200">
            Feedback
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;