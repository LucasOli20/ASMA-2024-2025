import React from 'react';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';
import Stats from './components/Stats';
import SubjectSelection from './components/SubjectSelection';
import { ChatProvider, useChat } from './contexts/ChatContext';
import { useState } from 'react';
import { BarChart2, MessageSquare, ArrowLeft } from 'lucide-react';

const MainContent: React.FC = () => {
  const [currentView, setCurrentView] = useState<'chat' | 'stats'>('chat');
  const { currentSubject, setCurrentSubject } = useChat();

  if (!currentSubject) {
    return <SubjectSelection />;
  }

  return (
    <>
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto flex items-center px-4">
          <button
            onClick={() => setCurrentSubject(null)}
            className="flex items-center px-4 py-3 text-gray-500 hover:text-gray-700 transition-colors duration-200"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Voltar para Disciplinas
          </button>
          <div className="h-10 w-px bg-gray-200 mx-4" />
          <button
            onClick={() => setCurrentView('chat')}
            className={`flex items-center px-4 py-3 border-b-2 text-sm font-medium transition-colors duration-200 ${
              currentView === 'chat'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <MessageSquare className="h-5 w-5 mr-2" />
            Conversar
          </button>
          <button
            onClick={() => setCurrentView('stats')}
            className={`flex items-center px-4 py-3 border-b-2 text-sm font-medium transition-colors duration-200 ${
              currentView === 'stats'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <BarChart2 className="h-5 w-5 mr-2" />
            Progresso
          </button>
        </div>
      </div>

      <main className="flex-1 overflow-y-auto bg-gray-50">
        {currentView === 'chat' ? <ChatInterface /> : <Stats />}
      </main>
    </>
  );
};

function App() {
  return (
    <ChatProvider>
      <div className="flex flex-col h-screen">
        <Header />
        <MainContent />
      </div>
    </ChatProvider>
  );
}

export default App;