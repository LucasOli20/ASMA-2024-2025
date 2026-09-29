import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, Edit2 } from 'lucide-react';
import { useChat } from '../contexts/ChatContext';

interface VoiceInputProps {
  onStartEditing: () => void;
  onStopEditing: () => void;
}

const VoiceInput: React.FC<VoiceInputProps> = ({ onStartEditing, onStopEditing }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editableText, setEditableText] = useState('');
  const [recordingDuration, setRecordingDuration] = useState(0);
  const { startVoiceRecording, stopVoiceRecording, transcription, sendTextMessage } = useChat();
  const timerRef = useRef<number>();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isRecording) {
      timerRef.current = window.setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
    } else {
      clearInterval(timerRef.current);
      setRecordingDuration(0);
    }
    
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isRecording]);

  useEffect(() => {
    if (transcription) {
      setEditableText(transcription);
    }
  }, [transcription]);

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [editableText, isEditing]);

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopVoiceRecording();
      setIsRecording(false);
      setIsEditing(true);
      onStartEditing();
    } else {
      setEditableText('');
      setIsEditing(false);
      onStopEditing();
      startVoiceRecording();
      setIsRecording(true);
    }
  };

  const handleSend = () => {
    if (editableText.trim()) {
      sendTextMessage(editableText.trim());
      setEditableText('');
      setIsEditing(false);
      onStopEditing();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative">
      <div className="flex items-center w-full gap-2">
        <button
          onClick={toggleRecording}
          className={`p-3 rounded-full transition-all duration-200 flex items-center justify-center ${
            isRecording 
              ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
              : 'bg-indigo-600 hover:bg-indigo-700'
          }`}
          title={isRecording ? "Parar gravação" : "Iniciar gravação"}
        >
          {isRecording ? (
            <MicOff className="h-5 w-5 text-white" />
          ) : (
            <Mic className="h-5 w-5 text-white" />
          )}
        </button>

        <div className="flex-1 relative">
          {isEditing ? (
            <div className="flex gap-2">
              <textarea
                ref={textareaRef}
                value={editableText}
                onChange={(e) => setEditableText(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1 px-4 py-2 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none min-h-[44px] max-h-[120px] shadow-sm"
                placeholder="Edite sua mensagem..."
              />
              <button
                onClick={handleSend}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
              >
                <Send className="h-5 w-5" />
                <span className="hidden sm:inline">Enviar</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <div className="flex-1 px-4 py-2 bg-white border border-gray-200 rounded-lg min-h-[44px] flex items-center text-gray-600">
                {isRecording ? (
                  <div className="flex items-center gap-3 w-full">
                    <div className="flex items-center gap-2">
                      <span className="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                      <span className="font-medium text-red-500">{formatDuration(recordingDuration)}</span>
                    </div>
                    <div className="flex-1 truncate">{transcription || "Ouvindo..."}</div>
                  </div>
                ) : (
                  <span className="text-gray-400">Clique no microfone para começar a gravar...</span>
                )}
              </div>
              {transcription && !isRecording && (
                <button
                  onClick={() => {
                    setIsEditing(true);
                    onStartEditing();
                  }}
                  className="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center"
                  title="Editar transcrição"
                >
                  <Edit2 className="h-5 w-5" />
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {isRecording && (
        <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 flex items-center gap-1 text-xs text-gray-500">
          <div className="flex gap-1">
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className="w-1 h-4 bg-red-500 rounded-full animate-pulse"
                style={{
                  animationDelay: `${i * 200}ms`,
                  opacity: 0.6 + (i * 0.2)
                }}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceInput;