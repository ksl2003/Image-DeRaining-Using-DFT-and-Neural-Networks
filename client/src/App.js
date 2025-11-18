import React, { useState } from 'react';
import './App.css';
import ImageUploader from './components/ImageUploader';
import ImageDisplay from './components/ImageDisplay';
import History from './components/History';

function App() {
  const [processedImages, setProcessedImages] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showHistory, setShowHistory] = useState(false);

  const handleImageProcessed = (data) => {
    setProcessedImages(data);
    setError(null);
  };

  const handleError = (err) => {
    setError(err);
    setProcessedImages(null);
  };

  const handleLoading = (isLoading) => {
    setLoading(isLoading);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🌧️ Image De-raining App</h1>
        <p>Upload a rainy image and let AI remove the rain for you!</p>
      </header>

      <main className="App-main">
        <div className="container">
          <div className="controls">
            <button 
              className="history-btn"
              onClick={() => setShowHistory(!showHistory)}
            >
              {showHistory ? 'Hide' : 'Show'} History
            </button>
          </div>

          {showHistory ? (
            <History />
          ) : (
            <>
              <ImageUploader
                onImageProcessed={handleImageProcessed}
                onError={handleError}
                onLoading={handleLoading}
                loading={loading}
              />

              {error && (
                <div className="error-message">
                  <p>❌ {error}</p>
                </div>
              )}

              {processedImages && (
                <ImageDisplay images={processedImages} />
              )}
            </>
          )}
        </div>
      </main>

      <footer className="App-footer">
        <p>Powered by Deep Learning & FastAPI</p>
      </footer>
    </div>
  );
}

export default App;

