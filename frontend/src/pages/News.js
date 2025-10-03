import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import { fetchArticles } from '../services/newsService';

// Helper function to format content with proper line breaks
const formatContent = (content, maxLength = null) => {
  if (!content) return '';
  
  // Replace \n\n with double line breaks and \n with single line breaks
  let formatted = content
    .replace(/\\n\\n/g, '\n\n')
    .replace(/\\n/g, '\n')
    .replace(/\n\n/g, '\n\n')
    .replace(/\n/g, '\n');
  
  // Truncate if maxLength is specified
  if (maxLength && formatted.length > maxLength) {
    formatted = formatted.substring(0, maxLength) + '...';
  }
  
  return formatted;
};

// Helper function to format dates to show only day and date
const formatDate = (dateString) => {
  if (!dateString) return '';
  
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  } catch (error) {
    console.error('Error formatting date:', error);
    return dateString; // Return original if parsing fails
  }
};

const News = () => {
  const { language } = useLanguage();
  const t = translations[language];
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    const loadArticles = async () => {
      try {
        setLoading(true);
        const data = await fetchArticles();
        setArticles(data.data.articles || []);
      } catch (err) {
        setError('Failed to load articles. Please try again later.');
        console.error('Error loading articles:', err);
      } finally {
        setLoading(false);
      }
    };

    loadArticles();
  }, []);

  // Helper function to get content based on language
  const getContent = (article) => {
    if (language === 'id') {
      return {
        title: article.title_id || article.title,
        content: article.content_id || article.content
      };
    }
    return {
      title: article.title,
      content: article.content
    };
  };

  // Filter articles by category
  const filteredArticles = articles.filter(article => {
    if (selectedCategory === 'all') return true;
    return article.category && article.category.includes(selectedCategory);
  });

  // Sort articles by importance and get the featured article
  const sortedArticles = filteredArticles.sort((a, b) => b.importance - a.importance);
  const featuredArticle = sortedArticles[0];
  const otherArticles = sortedArticles.slice(1);

  // Category filter options
  const categories = [
    { key: 'all', label: t.allNews, description: '' },
    { key: 'ECO', label: t.categoryEcoDesc, description: '' },
    { key: 'BNK', label: t.categoryBnkDesc, description: '' },
    { key: 'FIN', label: t.categoryFinDesc, description: '' },
    { key: 'MON', label: t.categoryMonDesc, description: '' },
    { key: 'MRK', label: t.categoryMrkDesc, description: '' }
  ];

  if (loading) {
    return (
      <div className="page-section">
        <div className="container">
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📰</div>
            <h2>{t.loadingNews}</h2>
            <p>{t.loadingNewsDesc}</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-section">
        <div className="container">
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚠️</div>
            <h2>{t.unableToLoadNews}</h2>
            <p>{error}</p>
            <button 
              className="btn btn-primary" 
              onClick={() => window.location.reload()}
              style={{ marginTop: '1rem' }}
            >
              {t.tryAgain}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <section className="page-section">
        <div className="container">
          <h2 style={{ textAlign: 'center', marginBottom: '3rem' }}>{t.financialNews}</h2>
          
          {/* Category Filter Buttons */}
          <div className="category-filters">
            {categories.map(category => (
              <button
                key={category.key}
                onClick={() => setSelectedCategory(category.key)}
                className={`category-btn ${selectedCategory === category.key ? 'active' : ''}`}
              >
                {category.label}
              </button>
            ))}
          </div>
          
          {/* Featured Article - Headline Design */}
          {featuredArticle && (() => {
            const content = getContent(featuredArticle);
            return (
              <div className="featured-article">
                <div className="featured-image-container">
                  <img 
                    src={featuredArticle.image_url} 
                    alt={content.title}
                    className="featured-image"
                  />
                  <div className="featured-overlay">
                    <div className="featured-content">
                      <span className="featured-badge">{t.topStory}</span>
                      <h1 className="featured-title">{content.title}</h1>
                      <p className="featured-excerpt" style={{ whiteSpace: 'pre-line' }}>
                        {formatContent(content.content, 200)}
                      </p>
                      <div className="featured-meta">
                        <span className="featured-date">{formatDate(featuredArticle.date)}</span>
                        <Link 
                          to={`/news/${featuredArticle._id}`}
                          className="btn btn-primary"
                        >
                          {t.readFullStory}
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })()}

          {/* No articles message */}
          {filteredArticles.length === 0 && (
            <div style={{ textAlign: 'center', padding: '4rem 0' }}>
              <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📰</div>
              <h3>No articles found</h3>
              <p>No articles available for the selected category.</p>
            </div>
          )}

          {/* Other Articles Grid */}
          {filteredArticles.length > 0 && (
            <div className="news-grid">
              {otherArticles.map(article => {
              const content = getContent(article);
              return (
                <article key={article._id} className="news-card">
                  <div className="news-image-container">
                    <img 
                      src={article.image_url} 
                      alt={content.title}
                      className="news-image"
                    />
                  </div>
                  <div className="news-content">
                    <div className="news-meta">
                      <span className="news-date">{formatDate(article.date)}</span>
                      <span className="news-importance">{t.importance}: {article.importance}/5</span>
                    </div>
                    <h3 className="news-title">{content.title}</h3>
                    <p className="news-excerpt" style={{ whiteSpace: 'pre-line' }}>
                      {formatContent(content.content, 150)}
                    </p>
                    <Link 
                      to={`/news/${article._id}`}
                      className="news-link"
                    >
                      {t.readMore}
                    </Link>
                  </div>
                </article>
              );
            })}
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default News;
