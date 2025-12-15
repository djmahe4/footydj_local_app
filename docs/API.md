# FootyDJ Local - API Documentation

This document describes the REST API endpoints provided by the FootyDJ Local backend server.

## Base URL

When running locally:
```
http://127.0.0.1:8000
```

## Authentication

Currently, the API uses a simple license-based authentication. You must activate your license before accessing analysis endpoints.

## Endpoints

### Health Check

Check if the server is running and responsive.

**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0.0"
}
```

**Status Codes**:
- `200 OK`: Server is healthy

---

### License Status

Check the current license activation status.

**Endpoint**: `GET /api/license-status`

**Response**:
```json
{
  "active": true,
  "activated_at": "2024-01-15T10:00:00.000Z",
  "expires_at": "2024-02-14T10:00:00.000Z"
}
```

**Response Fields**:
- `active` (boolean): Whether license is currently active
- `activated_at` (string): ISO timestamp of activation
- `expires_at` (string): ISO timestamp of expiration

**Status Codes**:
- `200 OK`: Status retrieved successfully

---

### Activate License

Activate the application with a license key.

**Endpoint**: `POST /api/activate`

**Request Body**:
```json
{
  "key": "XXXX-XXXX-XXXX-XXXX"
}
```

**Request Fields**:
- `key` (string, required): License key provided with purchase

**Response** (Success):
```json
{
  "success": true,
  "message": "License activated successfully",
  "expires_at": "2024-02-14T10:00:00.000Z"
}
```

**Response** (Error):
```json
{
  "detail": "Invalid license key"
}
```

**Status Codes**:
- `200 OK`: License activated successfully
- `400 Bad Request`: Invalid request (missing key)
- `403 Forbidden`: Invalid or expired license key
- `500 Internal Server Error`: Server error during activation

---

### Analyze Video

Upload and analyze a video file.

**Endpoint**: `POST /api/analyze-video`

**Request**:
- Content-Type: `multipart/form-data`
- Field: `video_file` (file)

**cURL Example**:
```bash
curl -X POST http://127.0.0.1:8000/api/analyze-video \
  -F "video_file=@/path/to/video.mp4"
```

**Python Example**:
```python
import requests

with open('video.mp4', 'rb') as f:
    files = {'video_file': f}
    response = requests.post(
        'http://127.0.0.1:8000/api/analyze-video',
        files=files
    )
    results = response.json()
```

**Response** (Success):
```json
{
  "success": true,
  "message": "Analysis completed successfully",
  "video_info": {
    "filename": "match_video.mp4",
    "status": "processed",
    "timestamp": "2024-01-15T10:30:00.000Z"
  },
  "analysis": {
    "field_detection": {
      "detected": true,
      "confidence": 0.95,
      "lines_detected": 12
    },
    "player_tracking": {
      "players_detected": 22,
      "teams_identified": 2,
      "tracking_quality": "high"
    },
    "ball_tracking": {
      "ball_detected": true,
      "tracking_confidence": 0.87,
      "possession_analyzed": true
    },
    "homography": {
      "calibrated": true,
      "transformation_quality": "excellent"
    }
  }
}
```

**Response Fields**:

**video_info**:
- `filename`: Name of the uploaded video
- `status`: Processing status
- `timestamp`: When analysis completed

**field_detection**:
- `detected` (boolean): Whether field was detected
- `confidence` (float): Detection confidence (0.0-1.0)
- `lines_detected` (int): Number of field lines found

**player_tracking**:
- `players_detected` (int): Total players identified
- `teams_identified` (int): Number of teams
- `tracking_quality` (string): Quality rating (high/medium/low)

**ball_tracking**:
- `ball_detected` (boolean): Whether ball was found
- `tracking_confidence` (float): Tracking confidence (0.0-1.0)
- `possession_analyzed` (boolean): Whether possession was determined

**homography**:
- `calibrated` (boolean): Whether camera calibration succeeded
- `transformation_quality` (string): Quality rating

**Response** (Error):
```json
{
  "detail": "Invalid video format"
}
```

**Status Codes**:
- `200 OK`: Analysis completed successfully
- `400 Bad Request`: Invalid file format or missing file
- `403 Forbidden`: License not activated
- `500 Internal Server Error`: Analysis failed

**Notes**:
- Maximum file size: 2GB
- Supported formats: MP4, MOV, AVI, MKV
- Processing time varies based on video length and hardware
- This endpoint processes the analysis part only (not trimming)

---

### Get Configuration

Retrieve current analysis configuration.

**Endpoint**: `GET /api/config`

**Response**:
```json
{
  "analyzer": {
    "lower_green": [30, 40, 40],
    "upper_green": [90, 255, 255],
    "morph_kernel_size": [5, 5],
    "min_contour_area_abs": 1000,
    "min_contour_area_ratio": 0.05,
    "angle_horizontal_tolerance": 25,
    "min_aspect_ratio_for_standard": 3.0,
    "max_aspect_ratio_for_standard": 0.3333333333333333
  },
  "homography": {
    "enabled": true,
    "yolo_model_path": "models/yolov8l_seg_37e.pt",
    "world_points_json_path": "line_endpoints.json",
    "confidence_threshold": 0.25,
    "ransac_reproj_thresh": 5.0,
    "homography_smoothing_alpha": 0.8,
    "update_interval_frames": 10,
    "min_points_for_homography": 4,
    "debug_draw_points": false
  },
  "player_analysis": {
    "enabled": true,
    "yolo_model_path": "models/best.pt",
    "confidence_threshold": 0.25,
    "reid_config": {
      "enabled": true,
      "save_rois": false
    }
  },
  "ball_analysis": {
    "enabled": true,
    "yolo_model_path": "models/yolov8m_ball_60e_1280.pt",
    "confidence_threshold": 0.3
  }
}
```

**Status Codes**:
- `200 OK`: Configuration retrieved successfully

---

### Get System Status

Get information about system capabilities and availability.

**Endpoint**: `GET /api/status`

**Response**:
```json
{
  "license_active": true,
  "modules_available": true,
  "models_available": {
    "yolov8l_seg_37e.pt": true,
    "best.pt": true,
    "yolov8m_ball_60e_1280.pt": true
  },
  "system_info": {
    "python_version": "3.11.0 (main, Oct 24 2022, 18:26:48) [MSC v.1933 64 bit (AMD64)]",
    "platform": "win32"
  }
}
```

**Response Fields**:
- `license_active` (boolean): Current license status
- `modules_available` (boolean): Whether analysis modules are loaded
- `models_available` (object): Status of each required model file
- `system_info` (object): Python and platform information

**Status Codes**:
- `200 OK`: Status retrieved successfully

---

## Error Handling

All API endpoints use standard HTTP status codes and return error details in JSON format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Status Codes**:
- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid request parameters
- `403 Forbidden`: Authentication/authorization failed
- `404 Not Found`: Endpoint doesn't exist
- `500 Internal Server Error`: Server-side error

## Rate Limiting

Currently, no rate limiting is implemented as the application runs locally.

## CORS

CORS is enabled for all origins in local mode. When deploying to production, configure appropriate CORS settings.

## WebSocket Support

WebSocket support for real-time progress updates is planned for future releases.

## Examples

### Complete Analysis Workflow

```python
import requests
import time

BASE_URL = 'http://127.0.0.1:8000'

# 1. Check server health
health = requests.get(f'{BASE_URL}/api/health').json()
print(f"Server status: {health['status']}")

# 2. Check license status
license_status = requests.get(f'{BASE_URL}/api/license-status').json()

if not license_status['active']:
    # 3. Activate license
    activate_response = requests.post(
        f'{BASE_URL}/api/activate',
        json={'key': 'YOUR-LICENSE-KEY'}
    )
    if activate_response.ok:
        print("License activated!")
    else:
        print("Activation failed:", activate_response.json())
        exit(1)

# 4. Get system status
status = requests.get(f'{BASE_URL}/api/status').json()
print(f"Modules available: {status['modules_available']}")

# 5. Analyze video
with open('match_video.mp4', 'rb') as f:
    files = {'video_file': f}
    print("Starting analysis...")
    response = requests.post(
        f'{BASE_URL}/api/analyze-video',
        files=files
    )

if response.ok:
    results = response.json()
    print("\nAnalysis Results:")
    print(f"Field detected: {results['analysis']['field_detection']['detected']}")
    print(f"Players tracked: {results['analysis']['player_tracking']['players_detected']}")
    print(f"Ball detected: {results['analysis']['ball_tracking']['ball_detected']}")
else:
    print("Analysis failed:", response.json())
```

### JavaScript/Fetch Example

```javascript
const BASE_URL = 'http://127.0.0.1:8000';

// Analyze video
async function analyzeVideo(videoFile) {
    const formData = new FormData();
    formData.append('video_file', videoFile);
    
    try {
        const response = await fetch(`${BASE_URL}/api/analyze-video`, {
            method: 'POST',
            body: formData
        });
        
        const results = await response.json();
        
        if (response.ok) {
            console.log('Analysis complete:', results);
            return results;
        } else {
            console.error('Analysis failed:', results.detail);
            return null;
        }
    } catch (error) {
        console.error('Request failed:', error);
        return null;
    }
}

// Usage
const fileInput = document.getElementById('video-upload');
fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const results = await analyzeVideo(file);
        // Handle results...
    }
});
```

## Support

For API-related questions or issues:
- Email: support@footydj.com
- GitHub Issues: github.com/djmahe4/footydj_local_app

---

**API Version**: 1.0.0  
**Last Updated**: January 2024
