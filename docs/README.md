# FootyDJ Local - Documentation

Welcome to the FootyDJ Local documentation! This guide will help you understand, install, and use the FootyDJ video analysis platform.

## 📚 Documentation Index

- **[Setup Guide](SETUP.md)** - Installation and initial configuration
- **[User Guide](USER_GUIDE.md)** - Comprehensive usage instructions
- **[API Documentation](API.md)** - REST API reference for integration

## 🎯 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   python build_tools/init_models.py
   ```

2. **Launch Application**
   ```bash
   python app/main.py
   ```

3. **Activate License**
   - Enter your license key in the License section
   - Start analyzing videos!

## 🖼️ Interface Screenshots

### License Activation
The first step is to activate your license to unlock the analysis features.

![License Page](https://github.com/user-attachments/assets/3dfe2fa0-5a87-4edc-984a-096c0963aae1)

### Settings & Configuration
Configure analysis parameters and view system information.

![Settings Page](https://github.com/user-attachments/assets/11940399-90f1-4f5e-9acc-e31449507bd1)

## 🚀 Key Features

### Video Analysis Pipeline
- **Field Detection**: Automatically identifies football field lines and boundaries
- **Player Tracking**: Tracks player positions and movements across frames
- **Ball Tracking**: Follows ball trajectory and analyzes possession
- **Camera Calibration**: Transforms video coordinates to real-world field positions

### Modern Web Interface
- **Responsive Design**: Beautiful, modern UI that works on desktop and mobile
- **Real-time Progress**: Live updates during video processing
- **Result Visualization**: Clear, organized display of analysis results
- **Easy Downloads**: Export results as JSON or annotated video

### Workflow Automation
- **Batch Processing**: Process multiple videos automatically
- **Command-line Tools**: Scriptable workflow for CI/CD integration
- **Flexible Configuration**: Customize analysis parameters via config files

## 📖 Usage Examples

### Basic Video Analysis

```python
import requests

# Start the server first: python app/server.py

# Activate license
response = requests.post('http://127.0.0.1:8000/api/activate', 
    json={'key': 'YOUR-LICENSE-KEY'})

# Analyze video
with open('match_video.mp4', 'rb') as f:
    files = {'video_file': f}
    result = requests.post('http://127.0.0.1:8000/api/analyze-video', 
        files=files)
    
print(result.json())
```

### Batch Processing with Workflow Script

```bash
# Place videos in fragments/ folder
python workflow.py

# View results in output/ folder
```

## 🏗️ Architecture

```
FootyDJ Local Application
├── Frontend (HTML/CSS/JavaScript)
│   ├── Modern, responsive UI
│   ├── Real-time progress tracking
│   └── Result visualization
│
├── Backend (FastAPI)
│   ├── REST API endpoints
│   ├── Video upload handling
│   └── Analysis orchestration
│
├── Analysis Engine (footydj5)
│   ├── Field detection
│   ├── Player tracking
│   ├── Ball tracking
│   └── Camera calibration
│
└── Desktop Wrapper (PyWebView)
    └── Native OS window
```

## 🔧 Configuration

Edit `app/config.py` to customize:

### Analysis Parameters
```python
ANALYZER_CONFIG = {
    "lower_green": [30, 40, 40],      # Grass color range
    "upper_green": [90, 255, 255],
    "min_contour_area_abs": 1000,     # Minimum field area
}
```

### Detection Thresholds
```python
PLAYER_ANALYSIS_CONFIG = {
    "confidence_threshold": 0.25,      # Player detection confidence
}

BALL_ANALYSIS_CONFIG = {
    "confidence_threshold": 0.3,       # Ball detection confidence
}
```

## 🎓 Best Practices

### Video Recording
- Use 1080p resolution minimum
- Maintain stable camera position
- Ensure good field visibility
- Record in good lighting conditions

### Processing
- Pre-trim videos to relevant segments
- Close unnecessary applications
- Use GPU if available
- Process shorter segments for faster results

## 🛠️ Troubleshooting

### Common Issues

**Problem**: License activation fails
- Check internet connection
- Verify license key is correct
- Ensure license hasn't expired

**Problem**: Field detection failing
- Improve camera angle
- Ensure field lines are visible
- Adjust green color thresholds in config

**Problem**: Slow processing
- Use GPU-enabled hardware
- Reduce video resolution
- Process shorter video segments

See [Setup Guide](SETUP.md) for detailed troubleshooting.

## 📊 Analysis Results

The system provides comprehensive analysis results:

### Field Detection
- Confidence score (0-100%)
- Number of lines detected
- Field type and dimensions

### Player Tracking
- Total players detected
- Team identification
- Tracking quality metrics

### Ball Tracking
- Detection confidence
- Tracking continuity
- Possession analysis

### Camera Calibration
- Homography quality
- Transformation accuracy
- Coordinate mapping

## 🔒 Security & Privacy

- **Local Processing**: All analysis runs on your machine
- **No Data Upload**: Videos never leave your computer
- **Encrypted Models**: YOLO models are protected
- **License Protection**: Secure activation system

## 🌟 Advanced Features

### API Integration
See [API Documentation](API.md) for:
- REST endpoint details
- Request/response formats
- Code examples in Python and JavaScript

### Workflow Automation
```bash
# Custom input/output directories
python workflow.py --fragments /path/to/videos --output /path/to/results

# Enable real analysis (requires compiled modules)
python workflow.py --real
```

### Custom Analysis
Create your own analysis scripts using the API:
```python
from app.server import analyze_video_mock

result = analyze_video_mock(
    video_path=Path("video.mp4"),
    output_dir=Path("output")
)
```

## 📝 File Structure

```
footydj_local_app/
├── app/
│   ├── main.py           # Desktop application entry point
│   ├── server.py         # FastAPI backend server
│   ├── config.py         # Configuration settings
│   └── footydj5/         # Analysis modules (compiled)
│
├── frontend/
│   ├── index.html        # Web interface
│   ├── style.css         # Styling
│   └── script.js         # Frontend logic
│
├── fragments/            # Input videos for batch processing
├── output/               # Analysis results
├── models/               # YOLO model files
├── docs/                 # Documentation (you are here!)
│   ├── README.md
│   ├── SETUP.md
│   ├── USER_GUIDE.md
│   └── API.md
│
├── workflow.py           # Batch processing script
└── requirements.txt      # Python dependencies
```

## 🤝 Support

Need help?

- **Email**: maheshwaranup@gmail.com
- **Documentation**: Read the guides in this folder
- **GitHub**: Report issues at github.com/djmahe4/footydj_local_app

## 📄 License

This software requires a valid license key to operate. Contact FootyDJ for licensing information.

---

**Version**: 1.0.0  
**Last Updated**: December 2025

**Happy Analyzing! ⚽**
