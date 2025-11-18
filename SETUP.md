# Setup Guide

## Quick Start

Follow these steps to set up and run the application:

### Step 1: Install Python Dependencies

```bash
cd backend/api
pip install -r requirements.txt
```

### Step 2: Install Node.js Dependencies

```bash
# Install Express server dependencies
cd ../../server
npm install

# Install React client dependencies
cd ../client
npm install
```

### Step 3: Set Up MongoDB

Make sure MongoDB is running on your system. You can:
- Install MongoDB locally, or
- Use MongoDB Atlas (cloud)

Update the connection string in `server/.env`:
```
MONGODB_URI=mongodb://localhost:27017/derain_app
```

### Step 4: Create Environment File

Copy the example environment file:
```bash
cd server
copy env.example .env
```

Edit `.env` and update if needed:
- `PORT=5000` (Express server port)
- `MONGODB_URI=mongodb://localhost:27017/derain_app`
- `FASTAPI_URL=http://localhost:8000`

### Step 5: Run the Application

You need to run three services in separate terminals:

#### Terminal 1: FastAPI Backend (Port 8000)
```bash
cd backend/api
python main.py
```

#### Terminal 2: Express Server (Port 5000)
```bash
cd server
npm start
```

#### Terminal 3: React Client (Port 3000)
```bash
cd client
npm start
```

### Step 6: Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

## Troubleshooting

### Model Weights
If you have trained model weights, place them as `model_weights.h5` in the `backend/api/` directory. The application will work without weights, but results may not be optimal.

### Port Conflicts
If any port is already in use:
- FastAPI: Change port in `backend/api/main.py` (line 118)
- Express: Change `PORT` in `server/.env`
- React: Change in `client/package.json` or use `PORT=3001 npm start`

### MongoDB Connection
- Ensure MongoDB is running: `mongod` or start MongoDB service
- Check connection string in `.env` file
- For MongoDB Atlas, use the connection string provided

### CORS Issues
If you encounter CORS errors, ensure:
- FastAPI CORS origins include `http://localhost:3000` and `http://localhost:5000`
- Express CORS is enabled (already configured)

## Development Mode

For development with auto-reload:

```bash
# FastAPI with auto-reload
cd backend/api
uvicorn main:app --reload --port 8000

# Express with nodemon
cd server
npm run dev

# React (already has hot-reload)
cd client
npm start
```

## Production Build

To build for production:

```bash
# Build React app
cd client
npm run build

# Serve the built files (you can use Express or any static server)
# The built files will be in client/build/
```

