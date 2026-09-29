import React, { useState } from 'react';
import { Check, Sparkles, BookOpen, ChevronRight, ChevronLeft } from 'lucide-react';

interface Correction {
  original: string;
  corrected: string;
  comment: string;
}

interface StyleImprovement {
  original: string;
  suggested: string;
  comment: string;
}

interface FigureOfSpeech {
  fragment: string;
  type: string;
  comment: string;
}

interface PortugueseAnalysis {
  corrections?: Correction[];
  style_improvements?: StyleImprovement[];
  figures_of_speech?: FigureOfSpeech[];
  full_answer?: string;
}

interface PortugueseCorrectionsProps {
  content: string;
}

const PortugueseCorrections: React.FC<PortugueseCorrectionsProps> = ({ content }) => {
  const [currentSection, setCurrentSection] = useState<'corrections' | 'style' | 'figures'>('corrections');
  const [isAnimating, setIsAnimating] = useState(true);

  let analysis: PortugueseAnalysis;
  try {
    analysis = JSON.parse(content) as PortugueseAnalysis;
  } catch (e) {
    console.error('Error parsing Portuguese analysis:', e);
    return null;
  }

  // Return null if there's no content to display
  if (!analysis.corrections?.length && !analysis.style_improvements?.length && !analysis.figures_of_speech?.length) {
    return null;
  }

  const sections = [
    {
      id: 'corrections',
      title: 'Correções',
      icon: Check,
      items: analysis.corrections || [],
      color: 'emerald',
      render: (item: Correction) => (
        <div className="space-y-2">
          <div className="flex items-start gap-2">
            <div className="text-red-500 line-through flex-1">{item.original}</div>
            <ChevronRight className="h-5 w-5 text-gray-400 mt-0.5" />
            <div className="text-emerald-600 flex-1">{item.corrected}</div>
          </div>
          <p className="text-sm text-gray-600 italic">{item.comment}</p>
        </div>
      )
    },
    {
      id: 'style',
      title: 'Melhorias de Estilo',
      icon: Sparkles,
      items: analysis.style_improvements || [],
      color: 'blue',
      render: (item: StyleImprovement) => (
        <div className="space-y-2">
          <div className="flex items-start gap-2">
            <div className="text-gray-500 flex-1">{item.original}</div>
            <ChevronRight className="h-5 w-5 text-gray-400 mt-0.5" />
            <div className="text-blue-600 flex-1">{item.suggested}</div>
          </div>
          <p className="text-sm text-gray-600 italic">{item.comment}</p>
        </div>
      )
    },
    {
      id: 'figures',
      title: 'Figuras de Estilo',
      icon: BookOpen,
      items: analysis.figures_of_speech || [],
      color: 'purple',
      render: (item: FigureOfSpeech) => (
        <div className="space-y-2">
          <div className="text-purple-600 font-medium">{item.fragment}</div>
          <div className="text-sm">
            <span className="font-medium">{item.type}:</span> {item.comment}
          </div>
        </div>
      )
    }
  ].filter(section => section.items.length > 0);

  // If no sections have items, don't render anything
  if (sections.length === 0) {
    return null;
  }

  // Ensure currentSection exists in available sections
  if (!sections.find(s => s.id === currentSection)) {
    setCurrentSection(sections[0].id as any);
  }

  const currentSectionData = sections.find(s => s.id === currentSection) || sections[0];
  const currentIndex = sections.findIndex(s => s.id === currentSection);

  const navigate = (direction: 'prev' | 'next') => {
    setIsAnimating(true);
    const newIndex = direction === 'next' ? 
      (currentIndex + 1) % sections.length : 
      (currentIndex - 1 + sections.length) % sections.length;
    setCurrentSection(sections[newIndex].id as any);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 my-4">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          {sections.map((section) => {
            const Icon = section.icon;
            return (
              <button
                key={section.id}
                onClick={() => {
                  setIsAnimating(true);
                  setCurrentSection(section.id as any);
                }}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  currentSection === section.id
                    ? `bg-${section.color}-50 text-${section.color}-600`
                    : 'text-gray-500 hover:bg-gray-50'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="hidden sm:inline">{section.title}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="min-h-[200px] relative overflow-hidden">
        <div
          className={`transform transition-all duration-500 ${
            isAnimating ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0'
          }`}
          onTransitionEnd={() => setIsAnimating(false)}
        >
          <div className="space-y-6">
            {currentSectionData.items.map((item, index) => (
              <div
                key={index}
                className="bg-gray-50 rounded-lg p-4"
              >
                {currentSectionData.render(item)}
              </div>
            ))}
          </div>
        </div>
      </div>

      {sections.length > 1 && (
        <div className="flex justify-between mt-6 pt-4 border-t">
          <button
            onClick={() => navigate('prev')}
            className="flex items-center gap-1 text-gray-600 hover:text-gray-800"
          >
            <ChevronLeft className="h-5 w-5" />
            Anterior
          </button>
          <button
            onClick={() => navigate('next')}
            className="flex items-center gap-1 text-gray-600 hover:text-gray-800"
          >
            Próximo
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      )}
    </div>
  );
};

export default PortugueseCorrections;