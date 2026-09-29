import React, { useState } from 'react';
import TextInput from './TextInput';
import VoiceInput from './VoiceInput';
import { MessageSquare, Mic } from 'lucide-react';
import { useChat } from '../contexts/ChatContext';

interface InputAreaProps {
  loading: boolean;
}

const InputArea: React.FC<InputAreaProps> = ({ loading }) => {
  const [inputMode, setInputMode] = useState<'text' | 'voice'>('text');
  const { transcription } = useChat();
  const [isEditing, setIsEditing] = useState(false);

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="max-w-4xl mx-auto">
        {transcription && !isEditing && inputMode === 'voice' && (
          <div className="mb-3 p-3 bg-purple-50 rounded-lg text-sm text-gray-700">
            <p className="font-medium text-purple-800 mb-1">Transcrição em tempo real:</p>
            <p>{transcription}</p>
          </div>
        )}
        
        <div className="flex items-center">
          <div className="flex space-x-2 mr-3">
            <button
              onClick={() => {
                setInputMode('text');
                setIsEditing(false);
              }}
              className={`p-2 rounded-full ${
                inputMode === 'text' 
                  ? 'bg-indigo-100 text-indigo-600' 
                  : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
              }`}
              aria-label="Modo texto"
              title="Modo texto"
            >
              <MessageSquare className="h-5 w-5" />
            </button>
            <button
              onClick={() => {
                setInputMode('voice');
                setIsEditing(false);
              }}
              className={`p-2 rounded-full ${
                inputMode === 'voice' 
                  ? 'bg-indigo-100 text-indigo-600' 
                  : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
              }`}
              aria-label="Modo voz"
              title="Modo voz"
            >
              <Mic className="h-5 w-5" />
            </button>
          </div>
          
          <div className="flex-1">
            {inputMode === 'text' ? (
              <TextInput loading={loading} />
            ) : (
              <VoiceInput onStartEditing={() => setIsEditing(true)} onStopEditing={() => setIsEditing(false)} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InputArea;