import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import TypingAnimation from '../components/TypingAnimation';

const Home = () => {
  const { language } = useLanguage();
  const t = translations[language];

  return (
    <div>
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h1>{t.heroTitle}</h1>
          <p>{t.heroSubtitle}</p>
          
          {/* AI Assistant Chat Box */}
          <div className="ai-chat-box">
            <div className="chat-message">
              <div className="chat-avatar">🤖</div>
              <div className="chat-content">
                <div className="chat-text" style={{ whiteSpace: 'pre-line' }}>
                  <TypingAnimation 
                    text={t.claudiaMessage} 
                    speed={15}
                    delay={1000}
                  />
                </div>
              </div>
            </div>
          </div>
          
          <Link to="/register" className="btn btn-primary" style={{ fontSize: '1.1rem', padding: '15px 30px' }}>
            Start Now
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="page-section">
        <div className="container">
          <h2>{t.whyChooseTitle}</h2>
          <div className="grid grid-3">
            <div className="card">
              <div style={{ fontSize: '3rem', marginBottom: '1rem', textAlign: 'center' }}>🤖</div>
              <h3>{t.aiConsultantTitle}</h3>
              <p>{t.aiConsultantDesc}</p>
            </div>
            <div className="card">
              <div style={{ fontSize: '3rem', marginBottom: '1rem', textAlign: 'center' }}>📰</div>
              <h3>{t.tailoredNewsTitle}</h3>
              <p>{t.tailoredNewsDesc}</p>
            </div>
            <div className="card">
              <div style={{ fontSize: '3rem', marginBottom: '1rem', textAlign: 'center' }}>⚖️</div>
              <h3>{t.bankCompareTitle}</h3>
              <p>{t.bankCompareDesc}</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="page-section" style={{ backgroundColor: '#f8f9fa' }}>
        <div className="container">
          <h2>{t.howItWorksTitle}</h2>
          <div className="grid grid-4">
            <div className="card">
              <div style={{ fontSize: '3rem', marginBottom: '1rem', textAlign: 'center' }}>📝</div>
              <h3>{t.step1Title}</h3>
              <p>{t.step1Desc}</p>
            </div>
            <div className="card">
              <div style={{ fontSize: '3rem', marginBottom: '1rem', textAlign: 'center' }}>💡</div>
              <h3>{t.step2Title}</h3>
              <p>{t.step2Desc}</p>
            </div>
            <div className="card">
              <div style={{ fontSize: '3rem', marginBottom: '1rem', textAlign: 'center' }}>🔔</div>
              <h3>{t.step3Title}</h3>
              <p>{t.step3Desc}</p>
            </div>
            <div className="card">
              <div style={{ fontSize: '3rem', marginBottom: '1rem', textAlign: 'center' }}>📈</div>
              <h3>{t.step4Title}</h3>
              <p>{t.step4Desc}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
