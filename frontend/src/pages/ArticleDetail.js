import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import { fetchArticleById } from '../services/newsService';

// Helper function to format content with proper line breaks
const formatContent = (content) => {
  if (!content) return '';
  
  // Replace \n\n with double line breaks and \n with single line breaks
  return content
    .replace(/\\n\\n/g, '\n\n')
    .replace(/\\n/g, '\n')
    .replace(/\n\n/g, '\n\n')
    .replace(/\n/g, '\n');
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

const ArticleDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { language } = useLanguage();
  const t = translations[language];
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadArticle = async () => {
      try {
        setLoading(true);
        const data = await fetchArticleById(id);
        setArticle(data.data || data); // Handle different response structures
      } catch (err) {
        setError('Failed to load article. Please try again later.');
        console.error('Error loading article:', err);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      loadArticle();
    }
  }, [id]);

  // Helper function to get content based on language
  const getContent = (article) => {
    if (!article) return { title: '', content: '' };
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

  if (loading) {
    return (
      <div className="page-section">
        <div className="container">
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📰</div>
            <h2>{t.loadingArticle}</h2>
            <p>{t.loadingArticleDesc}</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="page-section">
        <div className="container">
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚠️</div>
            <h2>{t.articleNotFound}</h2>
            <p>{error || 'The requested article could not be found.'}</p>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate('/news')}
              style={{ marginTop: '1rem' }}
            >
              {t.backToNews}
            </button>
          </div>
        </div>
      </div>
    );
  }

  const content = getContent(article);

  return (
    <div>
      <section className="page-section">
        <div className="container">
          {/* Back Button */}
          <button 
            className="btn btn-outline" 
            onClick={() => navigate('/news')}
            style={{ marginBottom: '2rem' }}
          >
            {t.backToNews}
          </button>

          {/* Article Header */}
          <div className="article-header">
            <div className="article-meta">
              <span className="article-date">{formatDate(article.date)}</span>
              <span className="article-importance">{t.importance}: {article.importance}/5</span>
            </div>
            <h1 className="article-title">{content.title}</h1>
            {article.image_url && (
              <div className="article-hero-image">
                <img 
                  src={article.image_url} 
                  alt={content.title}
                  className="hero-image"
                />
              </div>
            )}
          </div>

          {/* Article Content */}
          <div className="article-content">
            <div className="article-body">
              <p className="article-text" style={{ whiteSpace: 'pre-line' }}>{formatContent(content.content)}</p>
            </div>

            {/* Article Footer */}
            <div className="article-footer">
              <div className="article-actions">
                <a 
                  href={article.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="btn btn-primary"
                >
                  {t.readOriginalArticle}
                </a>
                <button 
                  className="btn btn-outline"
                  onClick={() => window.print()}
                >
                  {t.printArticle}
                </button>
              </div>
              
              <div className="article-info">
                <p><strong>{t.published}:</strong> {formatDate(article.date)}</p>
                <p><strong>{t.articleId}:</strong> {article._id}</p>
                {article.created_at && (
                  <p><strong>{t.created}:</strong> {new Date(article.created_at).toLocaleString()}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ArticleDetail;
