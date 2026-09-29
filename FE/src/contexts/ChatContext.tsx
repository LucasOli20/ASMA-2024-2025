import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';
import { Message, Subject } from '../types';
import { sendChatMessage, sendFeedback } from '../services/api';

interface ChatContextProps {
  messages: Message[];
  loading: boolean;
  transcription: string;
  currentSubject: Subject | null;
  setCurrentSubject: (subject: Subject | null) => void;
  sendTextMessage: (content: string) => Promise<void>;
  sendFeedbackResponse: (memoryId: number, feedback: string, suggestion?: string) => Promise<void>;
  startVoiceRecording: () => void;
  stopVoiceRecording: () => void;
}

const ChatContext = createContext<ChatContextProps | undefined>(undefined);

export const useChat = (): ChatContextProps => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

interface SubjectMessages {
  [key: string]: Message[];
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [messagesBySubject, setMessagesBySubject] = useState<SubjectMessages>({});
  const [loading, setLoading] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [currentSubject, setCurrentSubject] = useState<Subject | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const messages = currentSubject ? messagesBySubject[currentSubject] || [] : [];

  useEffect(() => {
    const eventSource = new EventSource("http://localhost:8000/events");
  
    let currentMessage = "";
    let timeout: NodeJS.Timeout;
    let lastMemoryId: number | null = null;
    const feedbackQueue: { text: string; memoryId: number }[] = [];
  
    const resetTimeout = () => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        if (currentMessage.trim() !== "" && currentSubject) {
          const assistantMessage: Message = {
            role: "assistant",
            content: currentMessage.trim(),
            memoryId: lastMemoryId || undefined,
          };
          
          setMessagesBySubject(prev => ({
            ...prev,
            [currentSubject]: [...(prev[currentSubject] || []), assistantMessage]
          }));
          
          currentMessage = "";

          while (feedbackQueue.length > 0) {
            const feedback = feedbackQueue.shift();
            if (feedback && currentSubject) {
              const feedbackMessage: Message = {
                role: "assistant",
                content: feedback.text,
                isFeedbackPrompt: true,
                memoryId: feedback.memoryId,
              };
              setMessagesBySubject(prev => ({
                ...prev,
                [currentSubject]: [...(prev[currentSubject] || []), feedbackMessage]
              }));
            }
          }
        }
      }, 600);
    };
  
    eventSource.onmessage = (event) => {
      if (event.data.startsWith("[MEMORY_ID]")) {
        lastMemoryId = parseInt(event.data.replace("[MEMORY_ID] ", "").trim(), 10);
      } else if (event.data.startsWith("[FEEDBACK]")) {
        try {
          const raw = event.data.replace("[FEEDBACK] ", "");
          const parsed = JSON.parse(raw);
          feedbackQueue.push({
            text: parsed.text,
            memoryId: parsed.memory_id,
          });
        } catch (err) {
          console.error("Erro ao processar mensagem de feedback:", err);
        }      
      } else {
        currentMessage += event.data + "\n";
        resetTimeout();
      }
    };
  
    eventSource.onerror = (err) => {
      console.error("SSE connection error:", err);
      eventSource.close();
    };
  
    return () => {
      clearTimeout(timeout);
      eventSource.close();
    };
  }, [currentSubject]);

  const sendTextMessage = async (content: string) => {
    if (!currentSubject) return;

    try {
      setLoading(true);
      const userMessage: Message = { role: 'user', content };
      
      setMessagesBySubject(prev => ({
        ...prev,
        [currentSubject]: [...(prev[currentSubject] || []), userMessage]
      }));
      
      await sendChatMessage(content, currentSubject);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = { 
        role: 'assistant', 
        content: 'Desculpe, ocorreu um erro ao processar a tua mensagem.' 
      };
      
      setMessagesBySubject(prev => ({
        ...prev,
        [currentSubject]: [...(prev[currentSubject] || []), errorMessage]
      }));
    } finally {
      setLoading(false);
    }
  };

  const sendFeedbackResponse = async (memoryId: number, feedback: string, suggestion?: string) => {
    try {
      await sendFeedback(memoryId, feedback, suggestion);
    } catch (error) {
      console.error('Erro ao enviar feedback:', error);
    }
  };

  const startVoiceRecording = () => {
    try {
      if (!('webkitSpeechRecognition' in window)) {
        alert('O teu navegador não suporta reconhecimento de voz.');
        return;
      }

      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }

      const SpeechRecognition = window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;

      recognition.lang = 'pt-PT';
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      let finalTranscript = '';

      recognition.onstart = () => {
        setTranscription('');
        finalTranscript = '';
      };

      recognition.onresult = (event) => {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }

        setTranscription(finalTranscript + interimTranscript);
      };

      recognition.onerror = (event) => {
        console.error('Erro no reconhecimento de voz:', event.error);
        if (event.error === 'not-allowed') {
          alert('Por favor, permite o acesso ao microfone para usar o reconhecimento de voz.');
        }
        recognition.stop();
        setTimeout(() => {
          try {
            recognition.start();
          } catch (e) {
            console.error('Failed to restart recognition:', e);
          }
        }, 1000);
      };

      recognition.onend = () => {
        if (recognitionRef.current === recognition) {
          try {
            recognition.start();
          } catch (e) {
            console.error('Failed to restart recognition:', e);
          }
        }
      };

      recognition.start();
    } catch (error) {
      console.error('Error starting voice recognition:', error);
      alert('Erro ao iniciar o reconhecimento de voz. Por favor, tenta novamente.');
    }
  };

  const stopVoiceRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
  };

  const value = {
    messages,
    loading,
    transcription,
    currentSubject,
    setCurrentSubject,
    sendTextMessage,
    sendFeedbackResponse,
    startVoiceRecording,
    stopVoiceRecording,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

declare global {
  interface Window {
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}