import React, { useState, useRef } from 'react';
import axios from 'axios';
import './ImageUploader.css';

const ImageUploader = ({ onImageProcessed, onError, onLoading, loading }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        onError('Please select a valid image file');
        return;
      }

      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        onError('File size must be less than 10MB');
        return;
      }

      setSelectedFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      onError('Please select an image first');
      return;
    }

    const formData = new FormData();
    formData.append('image', selectedFile);

    onLoading(true);
    onError(null);

    try {
      const response = await axios.post('/api/process-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        onImageProcessed({
          original: response.data.originalImage,
          derained: response.data.derainedImage,
        });
      } else {
        onError(response.data.error || 'Failed to process image');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.details || 
                          error.message || 
                          'Failed to process image. Please try again.';
      onError(errorMessage);
    } finally {
      onLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    onError(null);
  };

  return (
    <div className="image-uploader">
      <div className="upload-section">
        <div className="file-input-wrapper">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            ref={fileInputRef}
            className="file-input"
            id="file-input"
            disabled={loading}
          />
          <label htmlFor="file-input" className="file-input-label">
            {preview ? 'Change Image' : 'Choose Image'}
          </label>
        </div>

        {preview && (
          <div className="preview-section">
            <div className="preview-image-wrapper">
              <img src={preview} alt="Preview" className="preview-image" />
              <p className="preview-label">Selected Image</p>
            </div>
          </div>
        )}

        <div className="button-group">
          {selectedFile && (
            <>
              <button
                onClick={handleUpload}
                disabled={loading}
                className="upload-btn"
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Processing...
                  </>
                ) : (
                  '🚀 Process Image'
                )}
              </button>
              <button
                onClick={handleReset}
                disabled={loading}
                className="reset-btn"
              >
                Reset
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageUploader;

