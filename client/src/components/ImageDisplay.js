import React from 'react';
import './ImageDisplay.css';

const ImageDisplay = ({ images }) => {
  const handleDownload = (imageData, filename) => {
    const link = document.createElement('a');
    link.href = imageData;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="image-display">
      <h2 className="display-title">✨ Processing Results</h2>
      <div className="images-container">
        <div className="image-card">
          <h3 className="image-card-title">Original (Rainy)</h3>
          <div className="image-wrapper">
            <img 
              src={images.original} 
              alt="Original rainy image" 
              className="result-image"
            />
          </div>
          <button
            onClick={() => handleDownload(images.original, 'original-rainy.png')}
            className="download-btn"
          >
            📥 Download Original
          </button>
        </div>

        <div className="arrow">→</div>

        <div className="image-card">
          <h3 className="image-card-title">De-rained Result</h3>
          <div className="image-wrapper">
            <img 
              src={images.derained} 
              alt="De-rained image" 
              className="result-image"
            />
          </div>
          <button
            onClick={() => handleDownload(images.derained, 'derained-result.png')}
            className="download-btn"
          >
            📥 Download Result
          </button>
        </div>
      </div>
    </div>
  );
};

export default ImageDisplay;

