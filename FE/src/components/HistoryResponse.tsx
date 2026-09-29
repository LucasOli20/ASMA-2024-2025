import React, { useState, useEffect } from 'react';
import { Clock, ArrowRight, Users, Book } from 'lucide-react';
import HistoryTimeline from './HistoryTimeline';

interface TimelineEvent {
  date: string;
  event: string;
  description: string;
}

interface CauseEffect {
  cause: string;
  event: string;
  consequence: string;
}

interface HistoricalFigure {
  name: string;
  biography: string;
  importance: string;
}

interface GlossaryTerm {
  term: string;
  definition: string;
}

interface HistoryData {
  full_answer: string;
  timeline: TimelineEvent[];
  cause_effect: CauseEffect[];
  figures: HistoricalFigure[];
  glossary: GlossaryTerm[];
  book?: {
    title: string;
    url: string;
    author: string;
  };
}

interface HistoryResponseProps {
  content: string;
}

const HistoryResponse: React.FC<HistoryResponseProps> = ({ content }) => {
  let historyData: HistoryData;
  try {
    historyData = JSON.parse(content);
  } catch (e) {
    console.error('Error parsing history data:', e);
    return <div className="text-red-600">Erro ao processar a resposta histórica</div>;
  }

  // If there's no interactive content, just return the full answer
  if (
    !historyData.timeline.length &&
    !historyData.cause_effect.length &&
    !historyData.figures.length &&
    !historyData.glossary.length
  ) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 my-4">
        <p className="text-gray-800 whitespace-pre-line">{historyData.full_answer}</p>
        {historyData.book && (
          <div className="mt-4 p-4 bg-indigo-50 rounded-lg">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Book className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <h4 className="font-medium text-indigo-900">{historyData.book.title}</h4>
                <p className="text-sm text-indigo-700 mt-1">{historyData.book.author}</p>
                <a
                  href={historyData.book.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block mt-2 text-sm text-indigo-600 hover:text-indigo-800 underline"
                >
                  Ver livro recomendado
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <p className="text-gray-800 whitespace-pre-line">{historyData.full_answer}</p>
      </div>

      <HistoryTimeline
        timeline={historyData.timeline}
        causeEffect={historyData.cause_effect}
        figures={historyData.figures}
        glossary={historyData.glossary}
      />

      {historyData.book && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <Book className="h-5 w-5 text-indigo-600" />
            </div>
            <div>
              <h4 className="font-medium text-indigo-900">{historyData.book.title}</h4>
              <p className="text-sm text-indigo-700 mt-1">{historyData.book.author}</p>
              <a
                href={historyData.book.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block mt-2 text-sm text-indigo-600 hover:text-indigo-800 underline"
              >
                Ver livro recomendado
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryResponse;