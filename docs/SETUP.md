# FootyDJ Local - Setup Guide

This guide will help you set up and run the FootyDJ Local application on your machine.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Initial Setup](#initial-setup)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware Requirements
- **CPU**: Modern multi-core processor (Intel i5/AMD Ryzen 5 or better recommended)
- **RAM**: Minimum 8GB, 16GB recommended for optimal performance
- **Storage**: At least 5GB of free disk space for models and output files
- **GPU**: Optional but recommended for faster processing (CUDA-compatible NVIDIA GPU)

### Software Requirements
- **Operating System**: 
  - Windows 10/11 (64-bit)
  - macOS 10.14+ 
  - Linux (Ubuntu 20.04+ or equivalent)
- **Python**: Version 3.11.x (Note: Compiled modules are built for Python 3.11)
- **Internet Connection**: Required for initial license activation only

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/djmahe4/footydj_local_app.git
cd footydj_local_app
```

### Step 2: Set Up Python Environment

We recommend using a virtual environment:

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download Required Models

The application requires YOLO models for analysis. Download them using the provided script:

```bash
python build_tools/init_models.py
```

This will download the following models:
- `yolov8l_seg_37e.pt` - Field line detection and segmentation
- `best.pt` - Player detection and tracking
- `yolov8m_ball_60e_1280.pt` - Ball detection and tracking

Models will be stored in the `models/` directory (approximately 400MB total).

## Initial Setup

### Configuration

The application configuration is stored in `app/config.py`. You can modify various settings:

```python
# Example configuration options
APP_CONFIG = {
    "port": 8000,          # Web interface port
    "host": "127.0.0.1",   # Server host
}

ANALYZER_CONFIG = {
    # Field detection parameters
    "lower_green": [30, 40, 40],
    "upper_green": [90, 255, 255],
    # ... more settings
}
```

### License Key

You'll need a valid license key to use the application. If you don't have one:

1. Visit the FootyDJ website to purchase a license
2. Your license key will be sent to your email
3. Keep it handy for the activation step

## Running the Application

### Option 1: Desktop Application (Recommended)

Run the application as a standalone desktop app using pywebview:

```bash
python app/main.py
```

This will:
- Start the backend server on `http://127.0.0.1:8000`
- Open a native desktop window with the web interface
- Keep everything running locally on your machine

### Option 2: Web Browser Mode

If you prefer to use your web browser:

```bash
python app/server.py
```

Then open your browser and navigate to:
```
http://127.0.0.1:8000
```

### Option 3: Workflow Script (Batch Processing)

To process videos from the `fragments/` folder automatically:

```bash
# Process with mock analysis (for testing)
python workflow.py

# Process with real analysis (requires compiled modules)
python workflow.py --real

# Custom input/output directories
python workflow.py --fragments /path/to/videos --output /path/to/results
```

## First Run

### 1. License Activation

When you first launch the application:

1. The **License** section will be displayed
2. Enter your license key in the input field
3. Click **Activate License**
4. Wait for confirmation (requires internet connection)

Once activated, the license is valid for 30 days offline.

### 2. Processing Your First Video

After activation:

1. Click **Analyze Video** in the sidebar
2. Drag and drop a video file or click **Browse Files**
3. Supported formats: MP4, MOV, AVI, MKV
4. Click **Start Analysis**
5. Wait for processing to complete (time varies by video length)
6. View results in the **Results** section

### 3. Viewing Results

The analysis provides:
- **Field Detection**: Lines detected, confidence scores
- **Player Tracking**: Number of players, team identification
- **Ball Tracking**: Ball position, possession analysis
- **Camera Calibration**: Homography transformation quality

Download results as:
- **JSON**: Complete analysis data
- **Annotated Video**: Visualization with overlays (coming soon)

## Troubleshooting

### Common Issues

#### 1. Module Import Errors

**Problem**: `ImportError: DLL load failed` or similar module errors

**Solution**: 
- Ensure you're using Python 3.11.x
- Verify you're on the correct platform (Windows x64 for .pyd files)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

#### 2. Models Not Found

**Problem**: `Model file not found` error

**Solution**:
```bash
python build_tools/init_models.py
```

Verify models exist in `models/` directory.

#### 3. Port Already in Use

**Problem**: `Address already in use` error

**Solution**:
- Change the port in `app/config.py`
- Or kill the process using the port:
  ```bash
  # On Linux/Mac
  lsof -ti:8000 | xargs kill -9
  
  # On Windows
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```

#### 4. License Activation Failed

**Problem**: Cannot activate license

**Solution**:
- Check your internet connection
- Verify the license key is correct
- Ensure the license hasn't expired
- Contact support if the issue persists

#### 5. Slow Processing

**Problem**: Video analysis takes too long

**Solution**:
- Use a GPU-enabled machine for faster processing
- Reduce video resolution before processing
- Close other applications to free up resources
- Consider processing shorter video segments

### Getting Help

If you encounter issues not covered here:

1. Check the [User Guide](USER_GUIDE.md) for usage instructions
2. Review the [API Documentation](API.md) for technical details
3. Visit the GitHub repository issues page
4. Contact support@footydj.com

## Next Steps

- Read the [User Guide](USER_GUIDE.md) for detailed usage instructions
- Explore the [API Documentation](API.md) for integration options
- Check out example workflows in the repository

---

**Note**: This application runs entirely on your local machine. Your videos and data never leave your computer.
