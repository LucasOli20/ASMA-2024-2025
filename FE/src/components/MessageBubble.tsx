import React, { useState, useEffect } from 'react';
import { Message } from '../types';
import { User, Bot, Book } from 'lucide-react';
import { useChat } from '../contexts/ChatContext';
import SolutionSteps from './SolutionSteps';
import PortugueseCorrections from './PortugueseCorrections';
import HistoryTimeline from './HistoryTimeline';

interface MessageBubbleProps {
  message: Message;
}

interface MathSolution {
  full_answer: string;
  steps?: {
    title: string;
    explanation: string;
    formula?: string;
    values?: Record<string, number>;
  }[];
  book?: {
    title: string;
    author: string;
    url: string;
  };
}

interface HistorySolution {
  full_answer: string;
  timeline?: {
    date: string;
    event: string;
    description: string;
  }[];
  book?: {
    title: string;
    author: string;
    url: string;
  };
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  const [showSuggestionBox, setShowSuggestionBox] = useState(false);
  const [suggestion, setSuggestion] = useState('');
  const [displayedContent, setDisplayedContent] = useState('');
  const { sendFeedbackResponse, currentSubject } = useChat();

  const getMessageKey = (message: Message) => {
    return `message_animated_${message.memoryId || message.content}`;
  };

  const hasBeenAnimated = () => {
    return localStorage.getItem(getMessageKey(message)) === 'true';
  };

  const markAsAnimated = () => {
    localStorage.setItem(getMessageKey(message), 'true');
  };

  const formatText = (text: string) => {
    const lines = text.split('\n');
    let inNumberedList = false;
    let inBulletList = false;

    return lines.map((line, index) => {
      // Handle empty lines
      if (!line.trim()) {
        inNumberedList = false;
        inBulletList = false;
        return <div key={index} className="h-2" />;
      }

      // Handle numbered lists (e.g., "1. ", "2. ")
      const numberedMatch = line.match(/^(\d+)\.\s+(.*)/);
      if (numberedMatch) {
        const [, number, content] = numberedMatch;
        if (!inNumberedList) {
          inNumberedList = true;
          inBulletList = false;
        }
        return (
          <div key={index} className="flex items-start gap-2 mb-2 ml-4">
            <span className="font-semibold text-indigo-600 min-w-[1.5rem]">{number}.</span>
            <div className="flex-1">
              {formatInlineContent(content)}
            </div>
          </div>
        );
      }

      // Handle bullet points
      if (line.trim().startsWith('- ')) {
        if (!inBulletList) {
          inBulletList = true;
          inNumberedList = false;
        }
        return (
          <div key={index} className="flex items-start gap-2 mb-2 ml-4">
            <span className="w-2 h-2 rounded-full bg-indigo-500 mt-2" />
            <div className="flex-1">
              {formatInlineContent(line.slice(2))}
            </div>
          </div>
        );
      }

      // Reset list states for non-list content
      inNumberedList = false;
      inBulletList = false;

      // Handle regular paragraphs
      return (
        <div key={index} className="mb-2">
          {formatInlineContent(line)}
        </div>
      );
    });
  };

  const formatInlineContent = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        const content = part.slice(2, -2);
        return (
          <span key={index} className="font-semibold text-indigo-700">
            {content}
          </span>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  useEffect(() => {
    if (!isUser) {
      let text = '';
      try {
        const parsed = JSON.parse(message.content);
        text = parsed?.full_answer ?? '';
      } catch {
        text = message.content;
      }

      if (hasBeenAnimated()) {
        setDisplayedContent(text);
      } else {
        setDisplayedContent('');
        let content = '';
        let index = 0;

        const typeNextChar = () => {
          if (index < text.length) {
            content += text[index];
            setDisplayedContent(content);
            index++;
            const delay = text[index - 1] === '.' ? 100 : 10;
            setTimeout(typeNextChar, delay);
          } else {
            markAsAnimated();
          }
        };

        typeNextChar();
      }
    }
  }, [message.content, isUser]);

  const handleFeedback = async (value: "useful" | "not_useful") => {
    if (!message.memoryId) {
      console.error("Memory ID não disponível para esta mensagem de feedback.");
      return;
    }

    if (value === "not_useful") {
      setShowSuggestionBox(true);
      return;
    }

    try {
      await sendFeedbackResponse(message.memoryId, value);
      setFeedbackGiven(true);
    } catch (error) {
      console.error("Erro ao enviar feedback:", error);
    }
  };

  const submitSuggestion = async () => {
    if (!message.memoryId) return;

    try {
      await sendFeedbackResponse(message.memoryId, "not_useful", suggestion);
      setFeedbackGiven(true);
      setShowSuggestionBox(false);
    } catch (error) {
      console.error("Erro ao enviar sugestão:", error);
    }
  };

  const renderBookRecommendation = (book: MathSolution['book']) => {
    if (!book) return null;
    
    return (
      <div className="mt-3 p-4 bg-indigo-50 rounded-lg">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-indigo-100 rounded-lg">
            <Book className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h4 className="font-medium text-indigo-900">{book.title}</h4>
            <p className="text-sm text-indigo-700 mt-1">{book.author}</p>
            <a
              href={book.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-2 text-sm text-indigo-600 hover:text-indigo-800 underline"
            >
              Ver livro recomendado
            </a>
          </div>
        </div>
      </div>
    );
  };

  const renderMathSolution = (solution: MathSolution) => {
    if (!solution.steps?.length) return null;

    return (
      <div className="mt-4">
        <SolutionSteps steps={solution.steps} />
      </div>
    );
  };

  const parsedResponse = !isUser ? (() => {
    try {
      const parsed = JSON.parse(message.content);
      return {
        text: parsed.full_answer,
        isValid: true,
        raw: parsed
      };
    } catch (e) {
      return {
        text: message.content,
        isValid: false,
        raw: null
      };
    }
  })() : null;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
      <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} max-w-[80%] items-start gap-2`}>
        <div className={`h-8 w-8 rounded-full flex items-center justify-center ${isUser ? 'bg-indigo-100' : 'bg-purple-100'}`}>
          {isUser ? (
            <User className="h-5 w-5 text-indigo-600" />
          ) : (
            <Bot className="h-5 w-5 text-purple-600" />
          )}
        </div>
        <div className="flex flex-col gap-2">
          <div
            className={`px-4 py-3 rounded-2xl text-sm ${
              isUser
                ? 'bg-indigo-600 text-white rounded-tr-none'
                : 'bg-white text-gray-800 border border-gray-200 rounded-tl-none'
            }`}
          >
            {isUser ? message.content : formatText(displayedContent)}
          </div>

          {!isUser && parsedResponse?.isValid && (
            <div className="animate-slideUp">
              {currentSubject === 'matemática' && renderMathSolution(parsedResponse.raw)}
              {currentSubject === 'português' && (
                <PortugueseCorrections content={message.content} />
              )}
              {currentSubject === 'história' && parsedResponse.raw.timeline?.length > 0 && (
                <HistoryTimeline timeline={parsedResponse.raw.timeline} />
              )}
              {parsedResponse.raw.book && renderBookRecommendation(parsedResponse.raw.book)}
            </div>
          )}

          {!isUser && message.isFeedbackPrompt && !feedbackGiven && !showSuggestionBox && (
            <div className="flex gap-2 animate-fadeIn">
              <button
                className="px-3 py-1 text-sm rounded-lg bg-green-100 text-green-800 hover:bg-green-200 transition"
                onClick={() => handleFeedback("useful")}
              >
                👍 Sim
              </button>
              <button
                className="px-3 py-1 text-sm rounded-lg bg-red-100 text-red-800 hover:bg-red-200 transition"
                onClick={() => handleFeedback("not_useful")}
              >
                👎 Não
              </button>
            </div>
          )}

          {!isUser && message.isFeedbackPrompt && showSuggestionBox && !feedbackGiven && (
            <div className="mt-2 animate-fadeIn">
              <label className="text-sm font-medium text-gray-700">
                O que sugeres para melhorar?
              </label>
              <textarea
                className="w-full mt-1 p-2 border rounded-md"
                rows={3}
                value={suggestion}
                onChange={(e) => setSuggestion(e.target.value)}
              />
              <button
                className="mt-2 px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                onClick={submitSuggestion}
              >
                Enviar sugestão
              </button>
            </div>
          )}

          {!isUser && message.isFeedbackPrompt && feedbackGiven && (
            <div className="text-xs text-green-600 animate-fadeIn">Obrigado pelo feedback! ✅</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;