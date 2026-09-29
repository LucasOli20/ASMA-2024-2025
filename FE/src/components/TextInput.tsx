import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { useChat } from '../contexts/ChatContext';

interface TextInputProps {
  loading: boolean;
}

const TextInput: React.FC<TextInputProps> = ({ loading }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { sendTextMessage } = useChat();

  const handleSubmit = () => {
    if (message.trim() && !loading) {
      sendTextMessage(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    autoResize();
  };

  const autoResize = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto'; // reset
      textarea.style.height = `${textarea.scrollHeight}px`; // grow
    }
  };

  // reset altura quando apagas tudo
  useEffect(() => {
    autoResize();
  }, [message]);

  return (
    <form onSubmit={(e) => e.preventDefault()} className="flex items-end w-full gap-2">
      <textarea
        ref={textareaRef}
        value={message}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder="Escreva sua mensagem..."
        className="flex-1 px-4 py-2 bg-gray-100 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white resize-none overflow-hidden leading-relaxed"
        disabled={loading}
        rows={1}
      />
      <button
        type="button"
        disabled={!message.trim() || loading}
        onClick={handleSubmit}
        className={`px-4 py-2 bg-indigo-600 text-white rounded-full flex items-center justify-center ${
          !message.trim() || loading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-indigo-700'
        }`}
      >
        {loading ? (
          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        ) : (
          <Send className="h-5 w-5" />
        )}
      </button>
    </form>
  );
};

export default TextInput;
