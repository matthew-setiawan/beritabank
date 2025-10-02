import React, { useEffect, useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import { fetchBanks } from '../services/banksService';

const BankCompare = () => {
  const { language } = useLanguage();
  const t = translations[language];
  const [banks, setBanks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState({}); // {_id: boolean}

  useEffect(() => {
    const loadBanks = async () => {
      try {
        setLoading(true);
        const data = await fetchBanks();
        setBanks((data && data.data && data.data.banks) ? data.data.banks : []);
      } catch (err) {
        console.error(err);
        setError('Failed to load banks. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    loadBanks();
  }, []);

  const toggleExpand = (id) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  };

  // Helper function to get description based on language
  const getDescription = (bank) => {
    if (language === 'id') {
      return bank.desc_id || bank.desc;
    }
    return bank.desc;
  };

  if (loading) {
    return (
      <div className="page-section">
        <div className="container" style={{ textAlign: 'center', padding: '3rem 0' }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🏦</div>
          <h2>{t.loadingBanks}</h2>
          <p>{t.loadingBanksDesc}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-section">
        <div className="container" style={{ textAlign: 'center', padding: '3rem 0' }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚠️</div>
          <h2>{t.unableToLoadBanks}</h2>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={() => window.location.reload()} style={{ marginTop: '1rem' }}>{t.tryAgain}</button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <section className="page-section">
        <div className="container">
          <h2>{t.bankComparison}</h2>
          <p>{t.bankComparisonDesc}</p>

          <div className="grid grid-2">
            {banks.map(bank => (
              <div key={bank._id} className="card bank-card">
                {/* Header */}
                <div className="bank-card-header">
                  <div className="bank-brand">
                    {bank.logo_url ? (
                      <img src={bank.logo_url} alt={bank.name} className="bank-logo" />
                    ) : (
                      <div className="bank-logo-fallback">🏦</div>
                    )}
                    <div>
                      <h3 style={{ margin: 0 }}>{bank.name}</h3>
                      <div className="bank-meta-row">
                        <span className={`tag ${bank.bank_type === 'umum' ? 'tag-umum' : 'tag-bpr'}`}>
                          {bank.bank_type?.toUpperCase()}
                        </span>
                        <div className="app-methods">
                          {(bank.application_method || []).map((m, i) => (
                            <span key={i} className={`tag ${m.toLowerCase() === 'online' ? 'tag-online' : 'tag-branch'}`}>
                              {m}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bank-rating">
                    <span className="star">⭐</span>
                    <span className="rating-text">{bank.rating?.toFixed?.(1) ?? bank.rating}/5.0</span>
                  </div>
                </div>

                {/* Stats */}
                <div className="bank-stats">
                  <div className="stat">
                    <span className="stat-label">{t.interestRate}</span>
                    <span className="stat-value highlight">{bank.interest_rate}%</span>
                  </div>
                  {typeof bank.minimum_deposit !== 'undefined' && (
                    <div className="stat">
                      <span className="stat-label">{t.minimumDeposit}</span>
                      <span className="stat-value">Rp {bank.minimum_deposit?.toLocaleString?.('id-ID') ?? bank.minimum_deposit}</span>
                    </div>
                  )}
                  {Array.isArray(bank.tenure_options) && bank.tenure_options.length > 0 && (
                    <div className="stat">
                      <span className="stat-label">{t.tenure}</span>
                      <span className="stat-value">{bank.tenure_options.join(' / ')} {t.mo}</span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="bank-actions">
                  <button className="btn btn-outline" onClick={() => toggleExpand(bank._id)}>
                    {expanded[bank._id] ? t.hideDetails : t.viewDetails}
                  </button>
                  {bank.website_url && (
                    <a href={bank.website_url} target="_blank" rel="noopener noreferrer" className="btn btn-primary">
                      {t.visitWebsite}
                    </a>
                  )}
                </div>

                {/* Expandable Content */}
                {expanded[bank._id] && (
                  <div className="bank-details">
                    {bank.deposit_name && (
                      <div className="detail-row">
                        <span className="detail-label">{t.product}</span>
                        <span className="detail-value">{bank.deposit_name}</span>
                      </div>
                    )}
                    {bank.insurance && (
                      <div className="detail-row">
                        <span className="detail-label">{t.insurance}</span>
                        <span className="detail-value">{bank.insurance}</span>
                      </div>
                    )}
                    {typeof bank.fees !== 'undefined' && (
                      <div className="detail-row">
                        <span className="detail-label">{t.fees}</span>
                        <span className="detail-value">{bank.fees}</span>
                      </div>
                    )}
                    {getDescription(bank) && (
                      <div className="detail-desc">
                        {getDescription(bank)}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default BankCompare;
