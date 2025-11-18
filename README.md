# Image De-raining Web Application

A full-stack web application for removing rain from images using deep learning. Built with MERN stack (MongoDB, Express, React, Node.js) and FastAPI for ML model inference.

## 🏗️ Architecture

- **Frontend**: React.js (Port 3000)
- **Backend API**: Express.js (Port 5000)
- **ML API**: FastAPI (Port 8000)
- **Database**: MongoDB

## 📁 Project Structure

```
.
├── backend/
│   └── api/
│       ├── main.py              # FastAPI server
│       ├── model_utils.py        # Model utilities
│       └── requirements.txt      # Python dependencies
├── server/
│   ├── server.js                # Express server
│   ├── package.json             # Node.js dependencies
│   └── .env.example             # Environment variables template
├── client/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── App.js               # Main app component
│   │   └── index.js             # Entry point
│   └── package.json             # React dependencies
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB (local or Atlas)
- npm or yarn

### 1. FastAPI Backend Setup

```bash
cd backend/api

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
python main.py
# Or: uvicorn main:app --reload --port 8000
```

The FastAPI server will run on `http://localhost:8000`

### 2. Express Server Setup

```bash
cd server

# Install dependencies
npm install

# Create .env file from example
cp .env.example .env

# Edit .env file with your MongoDB URI
# MONGODB_URI=mongodb://localhost:27017/derain_app
# FASTAPI_URL=http://localhost:8000

# Run Express server
npm start
# Or for development: npm run dev
```

The Express server will run on `http://localhost:5000`

### 3. React Frontend Setup

```bash
cd client

# Install dependencies
npm install

# Run React app
npm start
```

The React app will run on `http://localhost:3000`

## 📝 Environment Variables

### Express Server (.env)

```env
PORT=5000
MONGODB_URI=mongodb://localhost:27017/derain_app
FASTAPI_URL=http://localhost:8000
```

## 🎯 Features

- ✅ Upload rainy images
- ✅ Process images using deep learning model
- ✅ Display original and de-rained images side-by-side
- ✅ Download processed images
- ✅ View processing history
- ✅ Responsive design

## 🔧 Model Information

The application uses a deep learning model based on:
- **D-Net**: Feature extraction network
- **N-Net**: Rain map prediction network
- **FFT-based processing**: Frequency domain transformations
- **Post-processing**: Image sharpening and enhancement

**Note**: The model weights need to be trained separately. If you have trained weights, save them as `model_weights.h5` in the `backend/api/` directory.

## 📦 Dependencies

### Python (FastAPI)
- fastapi
- uvicorn
- tensorflow
- numpy
- Pillow
- opencv-python

### Node.js (Express)
- express
- mongoose
- cors
- multer
- axios

### React
- react
- react-dom
- axios

## 🐛 Troubleshooting

1. **Model not loading**: Ensure TensorFlow is properly installed and model weights exist
2. **CORS errors**: Check that CORS origins are correctly configured in FastAPI
3. **MongoDB connection**: Verify MongoDB is running and connection string is correct
4. **Port conflicts**: Ensure ports 3000, 5000, and 8000 are available

## 📄 License

This project is for educational purposes.

## 👨‍💻 Development

To contribute or modify:

1. FastAPI endpoints: `backend/api/main.py`
2. Express routes: `server/server.js`
3. React components: `client/src/components/`
4. Model utilities: `backend/api/model_utils.py`

## 🔮 Future Enhancements

- [ ] User authentication
- [ ] Batch image processing
- [ ] Image comparison slider
- [ ] Performance metrics display
- [ ] Model retraining interface

