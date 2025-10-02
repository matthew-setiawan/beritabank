import React, { useState, useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import TypingAnimation from './TypingAnimation';

const OnboardingFlow = ({ onComplete }) => {
  const { language } = useLanguage();
  const t = translations[language];
  
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [showInput, setShowInput] = useState(false);
  const [isTyping, setIsTyping] = useState(true);

  const questions = [
    {
      key: 'financialGoals',
      question: t.financialGoalsQuestion,
      placeholder: t.financialGoalsPlaceholder
    },
    {
      key: 'banksUsed',
      question: t.banksUsedQuestion,
      placeholder: t.banksUsedPlaceholder
    },
    {
      key: 'currentInvestments',
      question: t.currentInvestmentsQuestion,
      placeholder: t.currentInvestmentsPlaceholder
    },
    {
      key: 'specificAssets',
      question: t.specificAssetsQuestion,
      placeholder: t.specificAssetsPlaceholder
    },
    {
      key: 'newsType',
      question: t.newsTypeQuestion,
      placeholder: t.newsTypePlaceholder
    },
    {
      key: 'newsRegion',
      question: t.newsRegionQuestion,
      placeholder: t.newsRegionPlaceholder
    }
  ];

  useEffect(() => {
    // Show input after typing animation completes
    const timer = setTimeout(() => {
      setIsTyping(false);
      setShowInput(true);
    }, 2000);
    return () => clearTimeout(timer);
  }, [currentStep]);

  const handleNext = () => {
    // Save current answer first
    const currentAnswerValue = currentAnswer.trim();
    if (currentAnswerValue) {
      setAnswers(prev => ({
        ...prev,
        [questions[currentStep].key]: currentAnswerValue
      }));
    }
    
    if (currentStep < questions.length - 1) {
      setCurrentStep(prev => prev + 1);
      setCurrentAnswer('');
      setIsTyping(true);
      setShowInput(false);
    } else {
      // Format answers as "question: answer" pairs
      // Include the current answer in the final description
      const allAnswers = {
        ...answers,
        [questions[currentStep].key]: currentAnswerValue
      };
      
      const formattedDesc = questions
        .map((q) => {
          const answer = allAnswers[q.key];
          return answer ? `${q.question}: ${answer}` : null;
        })
        .filter(Boolean)
        .join(', ');
      
      onComplete(formattedDesc);
    }
  };

  const handleSkip = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(prev => prev + 1);
      setCurrentAnswer('');
      setIsTyping(true);
      setShowInput(false);
    } else {
      // Format answers as "question: answer" pairs
      const formattedDesc = questions
        .map((q) => {
          const answer = answers[q.key];
          return answer ? `${q.question}: ${answer}` : null;
        })
        .filter(Boolean)
        .join(', ');
      
      onComplete(formattedDesc);
    }
  };

  const currentQuestion = questions[currentStep];

  return (
    <div className="onboarding-container">
      <div className="onboarding-card">
        <div className="onboarding-header">
          <div className="claudia-avatar">🤖</div>
          <h2 className="onboarding-title">{t.welcomeToOnboarding}</h2>
        </div>

        <div className="onboarding-content">
          {currentStep === 0 && (
            <div className="onboarding-intro">
              <TypingAnimation 
                text={t.onboardingIntro} 
                speed={30}
                delay={500}
              />
            </div>
          )}

          <div className="question-section">
            <div className="question-text">
              {isTyping ? (
                <TypingAnimation 
                  text={currentQuestion.question} 
                  speed={25}
                  delay={currentStep === 0 ? 3000 : 0}
                />
              ) : (
                currentQuestion.question
              )}
            </div>

            {showInput && (
              <div className="answer-input">
                <textarea
                  value={currentAnswer}
                  onChange={(e) => setCurrentAnswer(e.target.value)}
                  placeholder={currentQuestion.placeholder}
                  className="onboarding-textarea"
                  rows="3"
                  autoFocus
                />
              </div>
            )}

            {showInput && (
              <div className="onboarding-actions">
                <button 
                  type="button" 
                  className="btn btn-outline"
                  onClick={handleSkip}
                >
                  {t.skipQuestion}
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary"
                  onClick={handleNext}
                  disabled={!currentAnswer.trim()}
                >
                  {currentStep === questions.length - 1 ? t.finishOnboarding : t.nextQuestion}
                </button>
              </div>
            )}
          </div>

          <div className="progress-indicator">
            <span className="progress-text">
              {currentStep + 1} / {questions.length}
            </span>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${((currentStep + 1) / questions.length) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingFlow;
