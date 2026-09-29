import React from 'react';
import { Book, Calculator, History } from 'lucide-react';
import { useChat } from '../contexts/ChatContext';
import type { Subject } from '../types';

interface SubjectCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  subject: Subject;
  onClick: (subject: Subject) => void;
}

const SubjectCard: React.FC<SubjectCardProps> = ({ icon, title, description, subject, onClick }) => (
  <button
    onClick={() => onClick(subject)}
    className="relative bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 text-left group overflow-hidden"
  >
    <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
    <div className="relative">
      <div className="p-4 bg-indigo-100 rounded-2xl inline-block mb-6 group-hover:bg-indigo-200 transition-colors duration-300">
        {icon}
      </div>
      <h3 className="text-xl font-bold text-gray-800 mb-3">{title}</h3>
      <p className="text-gray-600">{description}</p>
      <div className="mt-6 inline-flex items-center text-indigo-600 font-medium">
        Iniciar aula
        <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  </button>
);

const SubjectSelection: React.FC = () => {
  const { setCurrentSubject } = useChat();

  const handleSubjectSelect = (subject: Subject) => {
    setCurrentSubject(subject);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-b from-gray-50 to-white flex items-center justify-center p-8">
      <div className="max-w-6xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Bem-vindo ao MentorAI
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Escolhe a tua disciplina e começa a aprender com os nossos professores especializados
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <SubjectCard
            icon={<History className="h-8 w-8 text-indigo-600" />}
            title="História"
            description="Explora civilizações antigas, revoluções importantes e acontecimentos que moldaram o nosso mundo. Aprende com as lições do passado."
            subject="história"
            onClick={handleSubjectSelect}
          />

          <SubjectCard
            icon={<Book className="h-8 w-8 text-indigo-600" />}
            title="Português"
            description="Domina a língua portuguesa, a gramática, a literatura e a escrita. Desenvolve as tuas competências de comunicação."
            subject="português"
            onClick={handleSubjectSelect}
          />

          <SubjectCard
            icon={<Calculator className="h-8 w-8 text-indigo-600" />}
            title="Matemática"
            description="Aprende álgebra, geometria e resolução de problemas. Desenvolve o pensamento lógico e capacidades analíticas."
            subject="matemática"
            onClick={handleSubjectSelect}
          />
        </div>

        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500">
            Os nossos professores virtuais utilizam inteligência artificial avançada para proporcionar uma experiência de aprendizagem personalizada
          </p>
        </div>
      </div>
    </div>
  );
};

export default SubjectSelection;
