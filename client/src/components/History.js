import React, { useState, useEffect } from 'react';
import API from '../api';
import './History.css';

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const response = await API.get('/api/history');
      if (response.data.success) {
        setHistory(response.data.images);
      }
    } catch (error) {
      setError('Failed to load history');
      console.error('History fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (imageData, filename) => {
    const link = document.createElement('a');
    link.href = imageData;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="history-container">
        <h2>Processing History</h2>
        <div className="loading">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-container">
        <h2>Processing History</h2>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="history-container">
      <h2>📜 Processing History</h2>
      {history.length === 0 ? (
        <div className="no-history">
          <p>No processing history yet. Upload an image to get started!</p>
        </div>
      ) : (
        <div className="history-grid">
          {history.map((item) => (
            <div key={item._id} className="history-item">
              <div className="history-header">
                <h4>{item.originalFilename}</h4>
                <span className={`status-badge ${item.status}`}>
                  {item.status}
                </span>
              </div>
              <p className="history-date">
                {new Date(item.processedAt).toLocaleString()}
              </p>
              {item.status === 'completed' && item.result && (
                <div className="history-images">
                  <div className="history-image-pair">
                    <div className="history-image-wrapper">
                      <img
                        src={item.result.originalImage}
                        alt="Original"
                        className="history-image"
                      />
                      <p className="image-label">Original</p>
                    </div>
                    <div className="history-image-wrapper">
                      <img
                        src={item.result.derainedImage}
                        alt="De-rained"
                        className="history-image"
                      />
                      <p className="image-label">De-rained</p>
                    </div>
                  </div>
                  <div className="history-actions">
                    <button
                      onClick={() =>
                        handleDownload(
                          item.result.derainedImage,
                          `derained-${item._id}.png`
                        )
                      }
                      className="history-download-btn"
                    >
                      📥 Download Result
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;

