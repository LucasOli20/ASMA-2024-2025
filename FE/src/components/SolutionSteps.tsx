import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';

interface Step {
  title: string;
  explanation: string;
  formula?: string;
  values?: Record<string, string | number>;
}

interface SolutionStepsProps {
  steps: Step[];
}

const SolutionSteps: React.FC<SolutionStepsProps> = ({ steps }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);

  const goToNextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
      setIsAnimating(true);
    }
  };

  const goToPreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      setIsAnimating(true);
    }
  };

  const resetSteps = () => {
    setCurrentStep(0);
    setIsAnimating(true);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 my-4">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-800">
          Passo {currentStep + 1} de {steps.length}
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={resetSteps}
            className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
            title="Recomeçar"
          >
            <RefreshCw className="h-5 w-5" />
          </button>
        </div>
      </div>

      <div className="min-h-[200px] relative overflow-hidden">
        <div
          className={`transform transition-all duration-500 ${
            isAnimating ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0'
          }`}
          onTransitionEnd={() => setIsAnimating(false)}
        >
          <h4 className="text-xl font-medium text-indigo-600 mb-3">
            {steps[currentStep].title}
          </h4>
          
          <p className="text-gray-700 mb-4 whitespace-pre-line">
            {steps[currentStep].explanation}
          </p>

          {steps[currentStep].formula && (
            <div className="bg-indigo-50 p-4 rounded-lg mb-4">
              <code className="text-lg font-mono text-indigo-700">
                {steps[currentStep].formula}
              </code>
            </div>
          )}

          {steps[currentStep].values && (
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="font-medium text-purple-800 mb-2">Valores:</p>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(steps[currentStep].values).map(([key, value]) => (
                  <div key={key} className="flex items-center gap-2">
                    <span className="font-mono text-purple-700">{key} =</span>
                    <span className="text-purple-900">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between mt-6 border-t pt-4">
        <button
          onClick={goToPreviousStep}
          disabled={currentStep === 0}
          className={`flex items-center gap-1 px-4 py-2 rounded-lg transition-colors ${
            currentStep === 0
              ? 'text-gray-400 cursor-not-allowed'
              : 'text-indigo-600 hover:bg-indigo-50'
          }`}
        >
          <ChevronLeft className="h-5 w-5" />
          Anterior
        </button>

        <div className="flex gap-1">
          {steps.map((_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full transition-colors ${
                index === currentStep ? 'bg-indigo-600' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>

        <button
          onClick={goToNextStep}
          disabled={currentStep === steps.length - 1}
          className={`flex items-center gap-1 px-4 py-2 rounded-lg transition-colors ${
            currentStep === steps.length - 1
              ? 'text-gray-400 cursor-not-allowed'
              : 'text-indigo-600 hover:bg-indigo-50'
          }`}
        >
          Próximo
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
};

export default SolutionSteps;