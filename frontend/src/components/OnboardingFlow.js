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
  const [bankSearch, setBankSearch] = useState('');
  const [showBankDropdown, setShowBankDropdown] = useState(false);
  const [selectedBank, setSelectedBank] = useState('');
  const [otherBank, setOtherBank] = useState('');

  // List of Indonesian banks
  const indonesianBanks = [
    'Bank Mandiri', 'Bank Central Asia (BCA)', 'Bank Rakyat Indonesia (BRI)', 'Bank Negara Indonesia (BNI)',
    'Bank CIMB Niaga', 'Bank Danamon', 'Bank Permata', 'Bank Maybank Indonesia', 'Bank OCBC NISP',
    'Bank UOB Indonesia', 'Bank Standard Chartered', 'Bank HSBC Indonesia', 'Bank Citibank Indonesia',
    'Bank Deutsche Bank Indonesia', 'Bank ANZ Indonesia', 'Bank Commonwealth', 'Bank DBS Indonesia',
    'Bank Mizuho Indonesia', 'Bank Sumitomo Mitsui Indonesia', 'Bank MUFG Indonesia', 'Bank Shinhan Indonesia',
    'Bank Woori Indonesia', 'Bank KEB Hana Indonesia', 'Bank BNP Paribas Indonesia', 'Bank Societe Generale Indonesia',
    'Bank Credit Agricole Indonesia', 'Bank BNP Paribas Indonesia', 'Bank BCA Syariah', 'Bank Mandiri Syariah',
    'Bank BRI Syariah', 'Bank BNI Syariah', 'Bank Muamalat Indonesia', 'Bank Syariah Indonesia (BSI)',
    'Bank Mega', 'Bank Panin', 'Bank Sinarmas', 'Bank Bukopin', 'Bank BTPN', 'Bank BTPN Syariah',
    'Bank Jateng', 'Bank Jatim', 'Bank Jateng Syariah', 'Bank Jatim Syariah', 'Bank Kalbar', 'Bank Kalsel',
    'Bank Kalteng', 'Bank Kaltim', 'Bank Kaltara', 'Bank Sulsel', 'Bank Sulut', 'Bank Sulteng',
    'Bank Sultra', 'Bank Gorontalo', 'Bank Sulbar', 'Bank Maluku', 'Bank Malut', 'Bank Papua',
    'Bank Papua Barat', 'Bank NTT', 'Bank NTB', 'Bank Bali', 'Bank Nusantara Parahyangan',
    'Bank Artha Graha Internasional', 'Bank Bumi Arta', 'Bank Capital Indonesia', 'Bank Centratama Nasional',
    'Bank Dinar Indonesia', 'Bank Ganesha', 'Bank Harda Internasional', 'Bank Ina Perdana',
    'Bank Index Selindo', 'Bank Jasa Jakarta', 'Bank Kesejahteraan Ekonomi', 'Bank Maspion Indonesia',
    'Bank Mayapada', 'Bank Mestika Dharma', 'Bank Metro Express', 'Bank Mitraniaga', 'Bank Multi Arta Sentosa',
    'Bank Nationalnobu', 'Bank Prima Express', 'Bank Royal Indonesia', 'Bank Sahabat Sampoerna',
    'Bank Sinar Harapan Bali', 'Bank Tabungan Negara (BTN)', 'Bank UOB Buana', 'Bank Victoria Internasional',
    'Bank Yudha Bakti', 'Bank Agris', 'Bank Bisnis Internasional', 'Bank Fama Internasional',
    'Bank Harda Internasional', 'Bank IBK Indonesia', 'Bank ICBC Indonesia', 'Bank Mayora',
    'Bank MNC Internasional', 'Bank Nobu', 'Bank Prima Master', 'Bank Sahabat Purba Danarta',
    'Bank Sampoerna', 'Bank Shinhan Indonesia', 'Bank Woori Saudara Indonesia 1906', 'Bank Yudha Bakti',
    'Bank Artos Indonesia', 'Bank Bisnis Internasional', 'Bank Fama Internasional', 'Bank Harda Internasional',
    'Bank IBK Indonesia', 'Bank ICBC Indonesia', 'Bank Mayora', 'Bank MNC Internasional', 'Bank Nobu',
    'Bank Prima Master', 'Bank Sahabat Purba Danarta', 'Bank Sampoerna', 'Bank Shinhan Indonesia',
    'Bank Woori Saudara Indonesia 1906', 'Bank Yudha Bakti', 'Bank Artos Indonesia', 'Bank Bisnis Internasional'
  ];

  const questions = [
    {
      key: 'banksUsed',
      question: t.banksUsedQuestion,
      placeholder: t.banksUsedPlaceholder,
      type: 'bankSelect'
    },
    {
      key: 'investmentTypes',
      question: t.investmentTypesQuestion,
      placeholder: t.investmentTypesPlaceholder,
      type: 'text'
    },
    {
      key: 'riskTolerance',
      question: t.riskToleranceQuestion,
      type: 'multipleChoice',
      options: t.riskToleranceOptions
    },
    {
      key: 'newsPresentation',
      question: t.newsPresentationQuestion,
      type: 'multipleChoice',
      options: t.newsPresentationOptions
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

  const handleOptionSelect = (optionKey, optionValue) => {
    setCurrentAnswer(optionValue);
    setAnswers(prev => ({
      ...prev,
      [questions[currentStep].key]: optionValue
    }));
  };

  // Filter banks based on search
  const filteredBanks = indonesianBanks.filter(bank =>
    bank.toLowerCase().includes(bankSearch.toLowerCase())
  );

  // Handle bank selection
  const handleBankSelect = (bank) => {
    if (bank === 'other') {
      setSelectedBank('other');
      setCurrentAnswer('other');
      setShowBankDropdown(false);
      setBankSearch('');
    } else {
      setSelectedBank(bank);
      setCurrentAnswer(bank);
      setShowBankDropdown(false);
      setBankSearch('');
    }
  };

  // Handle other bank input
  const handleOtherBankChange = (value) => {
    setOtherBank(value);
    setCurrentAnswer(value);
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
      
      onComplete(formattedDesc || 'User skipped all questions');
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
                {currentQuestion.type === 'text' ? (
                  <textarea
                    value={currentAnswer}
                    onChange={(e) => setCurrentAnswer(e.target.value)}
                    placeholder={currentQuestion.placeholder}
                    className="onboarding-textarea"
                    rows="3"
                    autoFocus
                  />
                ) : currentQuestion.type === 'bankSelect' ? (
                  <div className="bank-select-container">
                    <div className="bank-search-container">
                      <input
                        type="text"
                        value={bankSearch}
                        onChange={(e) => {
                          setBankSearch(e.target.value);
                          if (selectedBank !== 'other') {
                            setShowBankDropdown(true);
                          }
                        }}
                        onFocus={() => {
                          if (selectedBank !== 'other') {
                            setShowBankDropdown(true);
                          }
                        }}
                        placeholder={currentQuestion.placeholder}
                        className="bank-search-input"
                        autoFocus
                      />
                      {showBankDropdown && selectedBank !== 'other' && (
                        <div className="bank-dropdown">
                          {filteredBanks.slice(0, 10).map((bank, index) => (
                            <div
                              key={index}
                              className="bank-option"
                              onClick={() => handleBankSelect(bank)}
                            >
                              {bank}
                            </div>
                          ))}
                          <div
                            className="bank-option other-option"
                            onClick={() => handleBankSelect('other')}
                          >
                            {t.banksUsedOther}
                          </div>
                        </div>
                      )}
                    </div>
                    {selectedBank === 'other' && (
                      <div className="selected-bank other-selected">
                        Selected: Other
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedBank('');
                            setCurrentAnswer('');
                            setOtherBank('');
                            setShowBankDropdown(true);
                          }}
                          className="reset-selection-btn"
                        >
                          Change
                        </button>
                      </div>
                    )}
                    {selectedBank && selectedBank !== 'other' && (
                      <div className="selected-bank">
                        Selected: {selectedBank}
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedBank('');
                            setCurrentAnswer('');
                            setShowBankDropdown(true);
                          }}
                          className="reset-selection-btn"
                        >
                          Change
                        </button>
                      </div>
                    )}
                    {selectedBank === 'other' && (
                      <input
                        type="text"
                        value={otherBank}
                        onChange={(e) => handleOtherBankChange(e.target.value)}
                        placeholder="Enter your bank name..."
                        className="other-bank-input"
                      />
                    )}
                  </div>
                ) : (
                  <div className="multiple-choice-options">
                    {Object.entries(currentQuestion.options).map(([key, value]) => (
                      <button
                        key={key}
                        type="button"
                        className={`option-btn ${currentAnswer === value ? 'selected' : ''}`}
                        onClick={() => handleOptionSelect(key, value)}
                      >
                        {value}
                      </button>
                    ))}
                  </div>
                )}
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
