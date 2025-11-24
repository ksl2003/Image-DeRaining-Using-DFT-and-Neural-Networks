const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const axios = require('axios');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = 'uploads/';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif|webp/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only image files are allowed!'));
    }
  }
});

// MongoDB connection
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
  .then(() => console.log('✅ MongoDB connected'))
  .catch(err => console.error('❌ MongoDB connection error:', err));

// Image Schema
const imageSchema = new mongoose.Schema({
  originalFilename: { type: String, required: true },
  originalPath: { type: String, required: true },
  processedAt: { type: Date, default: Date.now },
  status: { type: String, enum: ['pending', 'processing', 'completed', 'failed'], default: 'pending' },
  result: {
    originalImage: String,
    derainedImage: String
  }
});

const Image = mongoose.model('Image', imageSchema);

// Routes
// Root health check
app.get('/', (req, res) => {
  res.json({ status: 'healthy', message: 'Express server is running' });
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', message: 'Express server is running' });
});

// Upload and process image
app.post('/api/process-image', upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No image file provided' });
    }

    // Create database entry
    const imageRecord = new Image({
      originalFilename: req.file.originalname,
      originalPath: req.file.path,
      status: 'processing'
    });
    await imageRecord.save();

    // Read file and send to FastAPI
    const fileStream = fs.createReadStream(req.file.path);
    const FormData = require('form-data');
    const formData = new FormData();
    formData.append('file', fileStream, {
      filename: req.file.originalname,
      contentType: req.file.mimetype
    });

    try {
      // Call FastAPI endpoint
      const response = await axios.post(`${FASTAPI_URL}/api/derain`, formData, {
        headers: {
          ...formData.getHeaders(),
        },
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
      });

      // Update database record
      imageRecord.status = 'completed';
      imageRecord.result = {
        originalImage: response.data.original_image,
        derainedImage: response.data.derained_image
      };
      await imageRecord.save();

      // Clean up uploaded file
      fs.unlinkSync(req.file.path);

      res.json({
        success: true,
        id: imageRecord._id,
        originalImage: response.data.original_image,
        derainedImage: response.data.derained_image,
        message: 'Image processed successfully'
      });

    } catch (error) {
      imageRecord.status = 'failed';
      await imageRecord.save();

      // Clean up uploaded file
      if (fs.existsSync(req.file.path)) {
        fs.unlinkSync(req.file.path);
      }

      console.error('FastAPI error:', error.response?.data || error.message);
      res.status(500).json({
        error: 'Failed to process image',
        details: error.response?.data?.detail || error.message
      });
    }

  } catch (error) {
    console.error('Server error:', error);
    res.status(500).json({ error: 'Server error', details: error.message });
  }
});

// Get processing history
app.get('/api/history', async (req, res) => {
  try {
    const images = await Image.find()
      .sort({ processedAt: -1 })
      .limit(50)
      .select('originalFilename processedAt status result');

    res.json({ success: true, images });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch history', details: error.message });
  }
});

// Get specific image by ID
app.get('/api/image/:id', async (req, res) => {
  try {
    const image = await Image.findById(req.params.id);
    if (!image) {
      return res.status(404).json({ error: 'Image not found' });
    }
    res.json({ success: true, image });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch image', details: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Express server running on port ${PORT}`);
  console.log(`📡 FastAPI URL: ${FASTAPI_URL}`);
});

