import React, { useState } from 'react';
import { Search, TrendingUp, X } from 'lucide-react';
import { mockVideos } from '../mockData';
import './Discover.css';

const Discover = ({ onBack }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const trendingHashtags = [
    { tag: 'fyp', views: '125.5B' },
    { tag: 'viral', views: '89.2B' },
    { tag: 'dance', views: '67.8B' },
    { tag: 'comedy', views: '45.3B' },
    { tag: 'food', views: '34.7B' },
    { tag: 'travel', views: '28.9B' }
  ];

  const handleSearch = (query) => {
    setSearchQuery(query);
    if (query.trim()) {
      const results = mockVideos.filter(video => 
        video.caption.toLowerCase().includes(query.toLowerCase()) ||
        video.username.toLowerCase().includes(query.toLowerCase())
      );
      setSearchResults(results);
    } else {
      setSearchResults([]);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
  };

  return (
    <div className="discover-page">
      {/* Search Header */}
      <div className="discover-header">
        <div className="search-container">
          <Search className="search-icon" size={20} />
          <input
            type="text"
            placeholder="Search"
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="search-input"
          />
          {searchQuery && (
            <button onClick={clearSearch} className="clear-button">
              <X size={20} />
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="discover-content">
        {searchResults.length > 0 ? (
          <div className="search-results">
            <h3 className="results-title">Search Results</h3>
            <div className="results-grid">
              {searchResults.map((video) => (
                <div 
                  key={video.id} 
                  className="result-item"
                  style={{ backgroundImage: `url(${video.thumbnailUrl})` }}
                >
                  <div className="result-overlay">
                    <span className="result-caption">{video.caption.slice(0, 40)}...</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="trending-section">
            <h2 className="section-title">
              <TrendingUp size={24} className="trending-icon" />
              Trending Hashtags
            </h2>
            <div className="hashtag-list">
              {trendingHashtags.map((item, index) => (
                <div key={index} className="hashtag-item">
                  <div className="hashtag-rank">{index + 1}</div>
                  <div className="hashtag-info">
                    <div className="hashtag-name">#{item.tag}</div>
                    <div className="hashtag-views">{item.views} views</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Discover;
