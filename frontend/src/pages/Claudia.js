import React, { useState, useEffect, useRef } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import { updateUserDescription, getPreferenceTags } from '../services/claudiaService';
import { getDailySummary } from '../services/dailySummaryService';
import TypingAnimation from '../components/TypingAnimation';

const Claudia = () => {
  const { language } = useLanguage();
  const t = translations[language];
  
  // Chat states
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Daily summary states
  const [dailySummary, setDailySummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [summaryError, setSummaryError] = useState(null);
  const [summaryDataLoading, setSummaryDataLoading] = useState(true);
  const [adviceDataLoading, setAdviceDataLoading] = useState(true);
  // Preferences minimized state controls header toggle and chat resizing
  const [preferencesMinimized, setPreferencesMinimized] = useState(true);
  // Preferences data states
  const [preferences, setPreferences] = useState({ banks: [], assets: [] });
  const [preferencesLoading, setPreferencesLoading] = useState(false);
  const [preferencesError, setPreferencesError] = useState(null);


  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Auto-resize textarea based on content
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const scrollHeight = textarea.scrollHeight;
      const maxHeight = 120; // Maximum height in pixels (about 5-6 lines)
      
      if (scrollHeight <= maxHeight) {
        textarea.style.height = scrollHeight + 'px';
        textarea.style.overflowY = 'hidden';
      } else {
        textarea.style.height = maxHeight + 'px';
        textarea.style.overflowY = 'auto';
      }
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputMessage]);

  useEffect(() => {
    // Load initial data when component mounts
    loadInitialData();
    loadPreferences();
  }, []);

  const loadInitialData = async () => {
    // Load daily summary from API
    await loadDailySummary();
    
    // Set initial chat message
    const dummyMessage = {
      id: Date.now(),
      role: 'assistant',
      content: language === 'en' 
        ? "Hello! I'm Claudia, your AI financial assistant. I'm here to help you with your financial questions and provide personalized advice based on your situation. How can I assist you today?"
        : "Halo! Saya Claudia, asisten keuangan AI Anda. Saya di sini untuk membantu Anda dengan pertanyaan keuangan dan memberikan saran yang dipersonalisasi berdasarkan situasi Anda. Bagaimana saya bisa membantu Anda hari ini?",
      timestamp: new Date().toISOString(),
      type: 'introduction'
    };
    setMessages([dummyMessage]);
  };

  const loadPreferences = async () => {
    setPreferencesLoading(true);
    setPreferencesError(null);
    try {
      const resp = await getPreferenceTags();
      const data = resp?.data || resp;
      setPreferences({
        banks: Array.isArray(data?.banks) ? data.banks : [],
        assets: Array.isArray(data?.assets) ? data.assets : [],
      });
    } catch (e) {
      setPreferencesError(e.message || 'Failed to load preference tags');
    } finally {
      setPreferencesLoading(false);
    }
  };

  // Load daily summary and preferences when language changes
  useEffect(() => {
    if (dailySummary) {
      loadDailySummary();
    }
    if (preferences.banks.length > 0 || preferences.assets.length > 0) {
      loadPreferences();
    }
  }, [language]);

  const loadDailySummary = async () => {
    setSummaryLoading(true);
    setSummaryDataLoading(true);
    setAdviceDataLoading(true);
    setSummaryError(null);
    
    try {
      const response = await getDailySummary();
      console.log('Daily Summary API Response:', response);
      // Access the nested data structure
      setDailySummary(response.data?.daily_summary || response);
      
      // Simulate separate loading for each section
      setTimeout(() => {
        setSummaryDataLoading(false);
      }, 500);
      
      setTimeout(() => {
        setAdviceDataLoading(false);
      }, 800);
      
    } catch (err) {
      console.error('Daily Summary Error:', err);
      setSummaryError(err.message || 'Failed to load daily summary');
      setSummaryDataLoading(false);
      setAdviceDataLoading(false);
    } finally {
      setSummaryLoading(false);
    }
  };


  const handleSendMessage = async (messageOverride) => {
    // Ensure we're working with strings and handle edge cases
    const messageText = messageOverride ?? inputMessage;
    const textToSend = typeof messageText === 'string' ? messageText.trim() : '';
    if (!textToSend || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: textToSend,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setShowSuggestions(false);
    setIsLoading(true);
    setIsTyping(true);
    setError(null);

    try {
      // Prepare conversation history as concatenated string
      const conversationHistory = messages
        .filter(msg => msg.role === 'user' || msg.role === 'assistant')
        .map(msg => `${msg.role}: ${msg.content}`)
        .join('\n');

      // Add current user message to history
      const fullConversationHistory = conversationHistory + 
        (conversationHistory ? '\n' : '') + 
        `user: ${textToSend}`;

      const response = await updateUserDescription(fullConversationHistory);
      
      if (response.success) {
        const assistantMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: response.message,
          timestamp: new Date().toISOString(),
          type: 'response'
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        
        // If daily summary was reset, reload both daily summary and preferences from API
        if (response.data?.daily_summary_reset) {
          loadDailySummary();
          loadPreferences();
        }
      } else {
        setError(response.error || 'Failed to update preferences');
      }
    } catch (err) {
      setError(err.message || 'Failed to send message');
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (text) => {
    if (isLoading) return;
    setShowSuggestions(false);
    handleSendMessage(text);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    try {
      return new Date(timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch {
      return '';
    }
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'short',
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  // Format text for summary and advice with bold text and newlines
  const formatText = (text) => {
    if (!text) return '';
    
    // Replace pipe characters with double newlines (paragraph spacing)
    let formatted = text.replace(/\|/g, '\n\n');
    
    // Handle bold text formatting with red color
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #dc3545;">$1</strong>');
    
    return formatted;
  };

  // Show main loading screen when initially loading
  if (summaryLoading || summaryDataLoading || adviceDataLoading) {
    return (
      <div className="main-loading-container">
        <div className="loading-spinner"></div>
        <h2>Loading content...</h2>
        <p>Please wait while we prepare your personalized experience</p>
      </div>
    );
  }

  return (
    <div className="claudia-page-container">
      {/* Daily Summary Section - 3/4 width */}
      <div className="daily-summary-section">
        {/* Summary and Advice - Top Half */}
        <div className="summary-content">
          {summaryError ? (
            <div className="summary-error">
              <p>{summaryError}</p>
              <button onClick={loadDailySummary} className="btn btn-primary">
                {t.tryAgain}
              </button>
            </div>
          ) : (
            <div className="summary-text-content">
              <div className="summary-paragraph">
                <h3>{t.dailySummary}</h3>
                {summaryDataLoading ? (
                  <div className="paragraph-loading">
                    <div className="loading-spinner"></div>
                    <p>Loading daily summary...</p>
                  </div>
                ) : (
                  <div 
                    dangerouslySetInnerHTML={{ 
                      __html: formatText(language === 'en' ? (dailySummary?.summary_en || dailySummary?.summary) : (dailySummary?.summary_id || dailySummary?.summary) || "No summary available")
                    }}
                    style={{ whiteSpace: 'pre-line' }}
                  />
                )}
              </div>
              <div className="advice-paragraph">
                <h3>{t.claudiaAdvice}</h3>
                {adviceDataLoading ? (
                  <div className="paragraph-loading">
                    <div className="loading-spinner"></div>
                    <p>Loading advice...</p>
                  </div>
                ) : (
                  <div 
                    dangerouslySetInnerHTML={{ 
                      __html: formatText(language === 'en' ? (dailySummary?.advice_en || dailySummary?.advice) : (dailySummary?.advice_id || dailySummary?.advice) || "No advice available")
                    }}
                    style={{ whiteSpace: 'pre-line' }}
                  />
                )}
              </div>
            </div>
          )}
        </div>

        {/* News Articles - Bottom Half */}
        <div className="news-articles-section">
          <h3>{t.relatedNews}</h3>
          <div className="news-articles-container">
            {summaryLoading ? (
              <div className="news-loading">
                <div className="loading-spinner"></div>
                <p>Loading related news...</p>
              </div>
            ) : dailySummary?.search_results?.length > 0 ? dailySummary.search_results.map((article, index) => (
              <div key={index} className="news-article-card">
                <div className="article-image">
                  <img src={article.image_url} alt={article.title} />
                </div>
                <div className="article-content">
                  <h4 className="article-title">
                    <a href={article.url} target="_blank" rel="noopener noreferrer">
                      {article.title}
                    </a>
                  </h4>
                  <p className="article-snippet">{article.snippet}</p>
                  <div className="article-meta">
                    <span className="article-date">{formatDate(article.date)}</span>
                  </div>
                </div>
              </div>
            )) : (
              <div className="no-articles">
                <p>No related news articles available at the moment.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Right Column - Preferences and Chat */}
      <div className="claudia-right-column">
        {/* Dummy Preferences - Above Chat */}
        <div className="dummy-preferences">
          <div className="dummy-pref-header">
            <div className="dummy-pref-title">Your Preferences</div>
            <div className="dummy-pref-subtitle">Use Claudia to adjust these preferences</div>
            <button 
              className="dummy-pref-toggle"
              onClick={() => setPreferencesMinimized(!preferencesMinimized)}
            >
              {preferencesMinimized ? '▲' : '▼'}
            </button>
          </div>
          {!preferencesMinimized && (
            <div className="dummy-pref-content">
              <div className="dummy-pref-row">
                <span className="dummy-pref-label">Banks:</span>
                <div className="dummy-pref-tags-scroll">
                  {preferencesLoading ? (
                    <span className="dummy-pref-tag bank" style={{ background: '#6c757d' }}>Loading...</span>
                  ) : preferencesError ? (
                    <span className="dummy-pref-tag bank" style={{ background: '#6c757d' }}>Failed to load</span>
                  ) : (preferences.banks && preferences.banks.length > 0 ? (
                    preferences.banks.map((bank, idx) => (
                      <span key={`bank-${idx}`} className="dummy-pref-tag bank">{bank}</span>
                    ))
                  ) : (
                    <span className="dummy-pref-tag bank" style={{ background: '#6c757d' }}>No banks</span>
                  ))}
                </div>
              </div>
              <div className="dummy-pref-row">
                <span className="dummy-pref-label">Assets:</span>
                <div className="dummy-pref-tags-scroll">
                  {preferencesLoading ? (
                    <span className="dummy-pref-tag asset" style={{ background: '#6c757d' }}>Loading...</span>
                  ) : preferencesError ? (
                    <span className="dummy-pref-tag asset" style={{ background: '#6c757d' }}>Failed to load</span>
                  ) : (preferences.assets && preferences.assets.length > 0 ? (
                    preferences.assets.map((asset, idx) => (
                      <span key={`asset-${idx}`} className="dummy-pref-tag asset">{asset}</span>
                    ))
                  ) : (
                    <span className="dummy-pref-tag asset" style={{ background: '#6c757d' }}>No assets</span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Chat Section - Below Preferences */}
        <div className={`claudia-chat-section ${preferencesMinimized ? 'expanded' : 'normal'}`}>
        <div className="claudia-chat-container">
          {/* Messages */}
          <div className="claudia-messages">
            {isLoading && messages.length === 0 && (
              <div className="claudia-welcome">
                <div className="claudia-welcome-avatar">🤖</div>
                <h2 className="claudia-welcome-title">{t.claudiaWelcome}</h2>
                <p className="claudia-welcome-subtitle">{t.claudiaSubtitle}</p>
                <div className="claudia-loading">
                  <div className="claudia-avatar-large">🤖</div>
                  <div>
                    <p>{t.loadingClaudia}</p>
                    <div className="claudia-loading-dots">
                      <div className="claudia-loading-dot"></div>
                      <div className="claudia-loading-dot"></div>
                      <div className="claudia-loading-dot"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="claudia-error">
                <p>{error}</p>
                <button 
                  className="btn btn-primary" 
                  onClick={loadInitialData}
                  style={{ marginTop: '1rem' }}
                >
                  {t.tryAgain}
                </button>
              </div>
            )}

            {messages.map((message) => (
              <div 
                key={message.id} 
                className={`claudia-message ${message.role}`}
              >
                <div className={`claudia-message-avatar ${message.role}`}>
                  {message.role === 'assistant' ? '🤖' : '👤'}
                </div>
                <div className={`claudia-message-content ${message.role}`}>
                  <p className="claudia-message-text">
                    {message.role === 'assistant' && message.id === messages[0]?.id ? (
                      <TypingAnimation 
                        text={message.content} 
                        speed={5}
                        delay={500}
                      />
                    ) : (
                      message.content
                    )}
                  </p>
                  <div className="claudia-message-time">
                    {formatTime(message.timestamp)}
                  </div>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="claudia-message">
                <div className="claudia-message-avatar assistant">🤖</div>
                <div className="claudia-message-content assistant">
                  <div className="claudia-loading">
                    <div className="claudia-loading-dots">
                      <div className="claudia-loading-dot"></div>
                      <div className="claudia-loading-dot"></div>
                      <div className="claudia-loading-dot"></div>
                    </div>
                    <span style={{ marginLeft: '1rem', color: '#666' }}>
                      {t.claudiaTyping}
                    </span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions Panel */}
          {showSuggestions && (
            <div className="suggestion-panel">
              <div className="suggestion-title">{t.suggestionTitle}</div>
              <div className="suggestion-chips">
                <button
                  type="button"
                  className="suggestion-chip"
                  onClick={() => handleSuggestionClick(t.suggestion1)}
                  disabled={isLoading}
                >
                  {t.suggestion1}
                </button>
                <button
                  type="button"
                  className="suggestion-chip"
                  onClick={() => handleSuggestionClick(t.suggestion2)}
                  disabled={isLoading}
                >
                  {t.suggestion2}
                </button>
                <button
                  type="button"
                  className="suggestion-chip"
                  onClick={() => handleSuggestionClick(t.suggestion3)}
                  disabled={isLoading}
                >
                  {t.suggestion3}
                </button>
              </div>
            </div>
          )}
          {/* Input */}
          <div className="claudia-input-container">
            <textarea
              ref={textareaRef}
              value={inputMessage}
              onChange={(e) => {
                setInputMessage(String(e.target.value || ''));
                adjustTextareaHeight();
              }}
              onKeyPress={handleKeyPress}
              placeholder={t.typeMessage}
              className="claudia-input"
              rows="1"
              disabled={isLoading}
              style={{
                resize: 'none',
                overflow: 'hidden',
                minHeight: '40px',
                maxHeight: '120px'
              }}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage || typeof inputMessage !== 'string' || !inputMessage.trim() || isLoading}
              className="claudia-send-button"
            >
              ➤
            </button>
          </div>
        </div>
      </div>
      </div>
    </div>
  );
};

export default Claudia;