import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';

interface TimelineEvent {
  date: string;
  event: string;
  description: string;
}

interface HistoryTimelineProps {
  timeline: TimelineEvent[];
}

const HistoryTimeline: React.FC<HistoryTimelineProps> = ({ timeline }) => {
  const [currentEvent, setCurrentEvent] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);

  const goToNextEvent = () => {
    if (currentEvent < timeline.length - 1) {
      setCurrentEvent(currentEvent + 1);
      setIsAnimating(true);
    }
  };

  const goToPreviousEvent = () => {
    if (currentEvent > 0) {
      setCurrentEvent(currentEvent - 1);
      setIsAnimating(true);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 my-4">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-800">
          Evento {currentEvent + 1} de {timeline.length}
        </h3>
      </div>

      <div className="min-h-[200px] relative overflow-hidden">
        <div
          className={`transform transition-all duration-500 ${
            isAnimating ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0'
          }`}
          onTransitionEnd={() => setIsAnimating(false)}
        >
          <div className="flex items-start gap-4">
            <div className="p-3 bg-amber-100 rounded-lg">
              <Calendar className="h-6 w-6 text-amber-600" />
            </div>
            <div>
              <div className="text-xl font-medium text-amber-600 mb-2">
                {timeline[currentEvent].date}
              </div>
              <h4 className="text-lg font-medium text-gray-900 mb-3">
                {timeline[currentEvent].event}
              </h4>
              <p className="text-gray-700 whitespace-pre-line">
                {timeline[currentEvent].description}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between mt-6 pt-4 border-t">
        <button
          onClick={goToPreviousEvent}
          disabled={currentEvent === 0}
          className={`flex items-center gap-1 px-4 py-2 rounded-lg transition-colors ${
            currentEvent === 0
              ? 'text-gray-400 cursor-not-allowed'
              : 'text-amber-600 hover:bg-amber-50'
          }`}
        >
          <ChevronLeft className="h-5 w-5" />
          Anterior
        </button>

        <div className="flex gap-1">
          {timeline.map((_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full transition-colors ${
                index === currentEvent ? 'bg-amber-600' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>

        <button
          onClick={goToNextEvent}
          disabled={currentEvent === timeline.length - 1}
          className={`flex items-center gap-1 px-4 py-2 rounded-lg transition-colors ${
            currentEvent === timeline.length - 1
              ? 'text-gray-400 cursor-not-allowed'
              : 'text-amber-600 hover:bg-amber-50'
          }`}
        >
          Próximo
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
};

export default HistoryTimeline;