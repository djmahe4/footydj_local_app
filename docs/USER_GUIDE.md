# FootyDJ Local - User Guide

Welcome to FootyDJ Local! This guide will help you get the most out of your video analysis platform.

## Table of Contents

- [Getting Started](#getting-started)
- [Interface Overview](#interface-overview)
- [Analyzing Videos](#analyzing-videos)
- [Understanding Results](#understanding-results)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [FAQs](#faqs)

## Getting Started

### First Time Setup

1. **Install and activate**: Follow the [Setup Guide](SETUP.md) to install dependencies and activate your license
2. **Prepare your videos**: Ensure videos are in supported formats (MP4, MOV, AVI, MKV)
3. **Launch the application**: Run `python app/main.py`

### What is FootyDJ?

FootyDJ is an advanced football/soccer video analysis tool that automatically:
- **Detects the field**: Identifies field lines and boundaries
- **Tracks players**: Monitors player positions and movements
- **Tracks the ball**: Follows ball trajectory and possession
- **Calibrates camera**: Creates homography transformation for tactical analysis

## Interface Overview

The application interface consists of four main sections:

### 1. License Section

**Purpose**: Activate and manage your license

**Features**:
- Enter license key
- View activation status
- Check expiration date

**Note**: License must be activated before analyzing videos. Activation requires internet connection once every 30 days.

### 2. Analyze Video Section

**Purpose**: Upload and process video files

**Features**:
- Drag-and-drop file upload
- File browser selection
- Real-time progress tracking
- Processing status updates

**Supported Formats**:
- MP4 (H.264/H.265)
- MOV (QuickTime)
- AVI
- MKV

**File Size**: Maximum 2GB per video

### 3. Results Section

**Purpose**: View and download analysis results

**Features**:
- Visual result cards for each analysis component
- Statistics and metrics
- Download options (JSON, annotated video)
- Historical results access

### 4. Settings Section

**Purpose**: Configure analysis parameters

**Features**:
- Enable/disable analysis components
- View system information
- Check module and model availability

## Analyzing Videos

### Step-by-Step Process

#### 1. Prepare Your Video

**Best Video Quality**:
- Resolution: 1280x720 (720p) minimum, 1920x1080 (1080p) recommended
- Frame rate: 25-30 fps optimal
- Codec: H.264 recommended
- Duration: 10 seconds to 90 minutes

**Camera Angle Requirements**:
- Side view of the field preferred
- Minimum 45-degree angle to the field
- Clear view of field lines
- Minimal camera movement (panning/zooming is okay)

**Lighting Conditions**:
- Daylight or stadium lighting preferred
- Avoid heavy shadows or overexposure
- Consistent lighting throughout video

#### 2. Upload Video

**Method A: Drag and Drop**
1. Navigate to the **Analyze Video** section
2. Drag your video file into the upload area
3. Release to upload

**Method B: File Browser**
1. Click **Browse Files** button
2. Select your video file
3. Click **Open**

#### 3. Start Analysis

1. Review the file information displayed
2. Click **Start Analysis** button
3. Monitor progress bar and status messages

**Processing Stages**:
- **Uploading**: Transferring video to processing pipeline
- **Field Detection**: Identifying field lines and boundaries
- **Camera Calibration**: Computing homography transformation
- **Player Tracking**: Detecting and tracking player movements
- **Ball Tracking**: Following ball trajectory
- **Finalizing**: Generating output files

**Processing Time**:
- Short clips (< 30 seconds): 1-3 minutes
- Medium videos (1-5 minutes): 5-15 minutes
- Long videos (> 5 minutes): 15+ minutes

*Processing time depends on video length, resolution, and hardware capabilities.*

#### 4. View Results

Once complete:
1. Navigate to the **Results** section automatically
2. Review the analysis cards
3. Download results as needed

## Understanding Results

### Field Detection Card

**Metrics**:
- **Confidence**: How certain the system is about field detection (0-100%)
  - 90-100%: Excellent
  - 70-90%: Good
  - < 70%: Fair (may need better camera angle)
- **Lines Found**: Number of field lines detected
  - 10-15: Complete field visible
  - 6-10: Partial field visible
  - < 6: Limited field view

**What it means**:
- High confidence and many lines = Better analysis accuracy
- Low values may indicate poor camera angle or field visibility

### Player Tracking Card

**Metrics**:
- **Players**: Total number of unique players detected
  - Typically 10-22 for standard matches
- **Teams**: Number of distinct teams identified
  - Usually 2 (plus referees as team 3)

**What it means**:
- Accurate player count indicates good detection
- Team identification enables tactical analysis
- Missing players may be due to occlusion or camera angle

### Ball Tracking Card

**Metrics**:
- **Confidence**: Ball detection certainty (0-100%)
  - 80-100%: Excellent tracking
  - 60-80%: Good tracking
  - < 60%: Fair tracking
- **Possession**: Whether possession analysis was performed
  - "Analyzed": Possession determined
  - "N/A": Unable to determine possession

**What it means**:
- High confidence = Accurate ball position tracking
- Possession analysis requires good ball and player tracking

### Camera Calibration Card

**Metrics**:
- **Quality**: Homography transformation quality
  - "Excellent": < 5 pixel reprojection error
  - "Good": 5-10 pixel error
  - "Fair": > 10 pixel error
- **Status**: Calibration success/failure

**What it means**:
- Good calibration enables coordinate transformation
- Transforms video coordinates to real-world field positions
- Essential for tactical analysis and metrics

## Advanced Features

### Batch Processing with Workflow Script

Process multiple videos automatically:

```bash
# Place videos in fragments/ folder
python workflow.py

# View output in output/ folder
```

**Benefits**:
- Process multiple videos without manual intervention
- Consistent settings across all videos
- Automated report generation

### Configuration Customization

Edit `app/config.py` to customize:

**Field Detection**:
```python
ANALYZER_CONFIG = {
    "lower_green": [30, 40, 40],  # Adjust for different grass colors
    "upper_green": [90, 255, 255],
    # ... more options
}
```

**Detection Confidence**:
```python
PLAYER_ANALYSIS_CONFIG = {
    "confidence_threshold": 0.25,  # Lower = more detections (but more false positives)
}
```

### API Integration

Use the REST API for custom integrations:

```python
import requests

# Analyze video via API
with open('video.mp4', 'rb') as f:
    files = {'video_file': f}
    response = requests.post('http://127.0.0.1:8000/api/analyze-video', files=files)
    results = response.json()
```

See [API Documentation](API.md) for complete reference.

## Best Practices

### Video Recording Tips

1. **Camera Position**:
   - Mount camera at elevated position
   - Side-line view of the field
   - Cover as much field as possible
   - Keep camera stable (tripod recommended)

2. **Recording Settings**:
   - Use highest quality setting available
   - 1080p resolution minimum
   - 30 fps frame rate
   - Avoid digital zoom

3. **Environmental Factors**:
   - Record in good lighting conditions
   - Avoid recording directly into sun
   - Check field line visibility before recording

### Processing Optimization

1. **Pre-processing**:
   - Trim videos to relevant segments
   - Convert to MP4 if in other formats
   - Ensure good field visibility

2. **System Resources**:
   - Close unnecessary applications
   - Ensure sufficient disk space for output
   - Use GPU if available for faster processing

3. **Quality vs Speed**:
   - Higher resolution = Better accuracy but slower processing
   - Consider downscaling very high resolution videos
   - Balance quality needs with processing time

### Result Interpretation

1. **Confidence Scores**:
   - > 80%: High confidence, reliable results
   - 60-80%: Moderate confidence, verify results
   - < 60%: Low confidence, consider re-recording

2. **Missing Data**:
   - Occlusions are normal (players blocking each other)
   - Temporary tracking loss is expected
   - Overall trends are more important than individual frames

3. **Validation**:
   - Spot-check results against original video
   - Verify player counts match actual game
   - Compare detection quality across different video segments

## FAQs

### General Questions

**Q: How long does analysis take?**
A: Depends on video length and hardware. Generally 2-5x video duration on average hardware.

**Q: Can I process multiple videos simultaneously?**
A: Currently, process one at a time in the UI. Use the workflow script for batch processing.

**Q: What happens to my videos?**
A: All processing is done locally. Videos never leave your computer.

**Q: Can I cancel processing?**
A: Yes, refresh the page or restart the application to cancel.

### Technical Questions

**Q: Why is field detection failing?**
A: Common causes:
- Poor camera angle
- Field lines not visible
- Non-standard field colors
- Heavy shadows or lighting issues

**Q: Why are some players not detected?**
A: Possible reasons:
- Players far from camera
- Occlusion (players blocking each other)
- Unusual uniforms or colors
- Low video quality

**Q: Can I use this for indoor football/futsal?**
A: Yes, but accuracy may vary. Indoor lighting and field markings differ from outdoor fields.

**Q: Does it work with amateur footage?**
A: Yes, but professional footage yields better results due to higher quality and better camera angles.

### Licensing Questions

**Q: How often do I need internet connection?**
A: Once every 30 days to reactivate your license. Otherwise, fully offline.

**Q: Can I transfer my license to another computer?**
A: Yes, deactivate on one computer and activate on another.

**Q: What happens if my license expires?**
A: You'll need to renew to continue using the application.

## Support

Need help? Contact us:

- **Email**: support@footydj.com
- **Documentation**: Check the [Setup Guide](SETUP.md) and [API Docs](API.md)
- **GitHub**: Report issues at github.com/djmahe4/footydj_local_app

---

**Happy Analyzing! ⚽**
