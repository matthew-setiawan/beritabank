import React, { useEffect, useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import { fetchBanks } from '../services/banksService';

const BankCompare = () => {
  const { language } = useLanguage();
  const t = translations[language];
  const [banks, setBanks] = useState([]);
  const [filteredBanks, setFilteredBanks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState({}); // {_id: boolean}
  const [sortBy, setSortBy] = useState('interest_rate');
  const [sortOrder, setSortOrder] = useState('high_to_low');
  const [filters, setFilters] = useState({
    applicationMethod: ['Online', 'Branch'], // Default: all checked
    bankType: ['umum', 'bpr'] // Default: all checked
  });

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

  // Filter and sort banks
  useEffect(() => {
    let filtered = [...banks];

    // Apply filters
    if (filters.applicationMethod.length > 0) {
      filtered = filtered.filter(bank => 
        bank.application_method && 
        filters.applicationMethod.some(method => bank.application_method.includes(method))
      );
    }

    if (filters.bankType.length > 0) {
      filtered = filtered.filter(bank => 
        bank.bank_type && filters.bankType.includes(bank.bank_type)
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue, bValue;

      switch (sortBy) {
        case 'interest_rate':
          aValue = parseFloat(a.interest_rate) || 0;
          bValue = parseFloat(b.interest_rate) || 0;
          break;
        case 'rating':
          aValue = parseFloat(a.rating) || 0;
          bValue = parseFloat(b.rating) || 0;
          break;
        case 'risk':
          // Sort risk by logical order: Low (0), Medium (1), High (2)
          const riskOrder = { 'low': 0, 'medium': 1, 'high': 2 };
          aValue = riskOrder[(a.risk || '').toLowerCase()] ?? 999; // Unknown risks go to end
          bValue = riskOrder[(b.risk || '').toLowerCase()] ?? 999;
          break;
        default:
          return 0;
      }

      // Handle different sort orders based on field type
      if (sortBy === 'interest_rate') {
        if (sortOrder === 'high_to_low') {
          return bValue - aValue; // Higher rates first
        } else {
          return aValue - bValue; // Lower rates first
        }
      } else if (sortBy === 'rating') {
        if (sortOrder === 'high_to_low') {
          return bValue - aValue; // Higher ratings first
        } else {
          return aValue - bValue; // Lower ratings first
        }
      } else if (sortBy === 'risk') {
        if (sortOrder === 'low_to_high') {
          return aValue - bValue; // Low risk first
        } else {
          return bValue - aValue; // High risk first
        }
      }
      
      return 0;
    });

    setFilteredBanks(filtered);
  }, [banks, sortBy, sortOrder, filters]);

  const toggleExpand = (id) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const handleFilterChange = (filterType, value, checked) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: checked 
        ? [...prev[filterType], value]
        : prev[filterType].filter(item => item !== value)
    }));
  };

  const handleSortByChange = (newSortBy) => {
    setSortBy(newSortBy);
    // Set appropriate default sort order for each field
    if (newSortBy === 'interest_rate') {
      setSortOrder('high_to_low');
    } else if (newSortBy === 'rating') {
      setSortOrder('high_to_low');
    } else if (newSortBy === 'risk') {
      setSortOrder('low_to_high');
    }
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

          {/* Filter and Sort Controls */}
          <div className="bank-controls">
            <div className="control-group">
              <label>{t.sortBy}:</label>
              <select 
                value={sortBy} 
                onChange={(e) => handleSortByChange(e.target.value)}
                className="control-select"
              >
                <option value="interest_rate">{t.sortByInterestRate}</option>
                <option value="rating">{t.sortByRating}</option>
                <option value="risk">{t.sortByRisk}</option>
              </select>
              <select 
                value={sortOrder} 
                onChange={(e) => setSortOrder(e.target.value)}
                className="control-select"
              >
                {sortBy === 'risk' ? (
                  <>
                    <option value="low_to_high">{t.sortOrderLowToHigh}</option>
                    <option value="high_to_low">{t.sortOrderHighToLow}</option>
                  </>
                ) : (
                  <>
                    <option value="high_to_low">{t.sortOrderHighToLow}</option>
                    <option value="low_to_high">{t.sortOrderLowToHigh}</option>
                  </>
                )}
              </select>
            </div>

            <div className="control-group">
              <label>{t.filterBy}:</label>
              <div className="filter-checkboxes">
                <div className="checkbox-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.applicationMethod.includes('Online')}
                      onChange={(e) => handleFilterChange('applicationMethod', 'Online', e.target.checked)}
                    />
                    <span>{t.filterOnline}</span>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.applicationMethod.includes('Branch')}
                      onChange={(e) => handleFilterChange('applicationMethod', 'Branch', e.target.checked)}
                    />
                    <span>{t.filterBranch}</span>
                  </label>
                </div>
                <div className="checkbox-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.bankType.includes('umum')}
                      onChange={(e) => handleFilterChange('bankType', 'umum', e.target.checked)}
                    />
                    <span>{t.filterUmum}</span>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.bankType.includes('bpr')}
                      onChange={(e) => handleFilterChange('bankType', 'bpr', e.target.checked)}
                    />
                    <span>{t.filterBpr}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-2">
            {filteredBanks.map(bank => (
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
                  {bank.risk && (
                    <div className="stat">
                      <span className="stat-label">{t.risk}</span>
                      <span className="stat-value">{bank.risk}</span>
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
