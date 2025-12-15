# FootyDJ Local - Workflow Guide

This guide explains how to use the automated workflow system to process videos efficiently.

## Overview

The workflow system provides automated batch processing of football match videos with minimal manual intervention. It's perfect for:

- Processing multiple videos at once
- Automating analysis for regular recordings
- Integration with CI/CD pipelines
- Scripted analysis workflows

## Quick Start

### Basic Usage

```bash
# Process videos from the fragments/ folder
python workflow.py

# Output will be saved to output/ folder with timestamp
```

### With Custom Directories

```bash
# Specify input and output directories
python workflow.py --fragments /path/to/videos --output /path/to/results
```

### Real Analysis Mode

```bash
# Attempt to use real analysis modules (requires compiled .pyd files)
python workflow.py --real
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--fragments` | Directory containing input videos | `fragments` |
| `--output` | Base directory for output files | `output` |
| `--real` | Attempt real analysis (falls back to mock if unavailable) | False |

## Workflow Process

### 1. Video Discovery

The workflow automatically finds all video files in the specified directory:

```
Supported formats:
- MP4 (.mp4)
- MOV (.mov)
- AVI (.avi)
- MKV (.mkv)
```

### 2. Processing Pipeline

For each video, the workflow executes:

1. **Load Video**: Opens and validates the video file
2. **Field Detection**: Identifies field lines and boundaries
3. **Camera Calibration**: Computes homography transformation
4. **Player Tracking**: Detects and tracks player movements
5. **Ball Tracking**: Follows ball trajectory and possession
6. **Output Generation**: Creates JSON results and CSV tracking data

### 3. Output Structure

```
output/
└── analysis_20241215_143000/
    ├── video1_results.json          # Complete analysis results
    ├── video1_tracking.csv          # Frame-by-frame tracking data
    ├── video1_annotated.mp4         # Visualized output (planned)
    ├── video2_results.json
    ├── video2_tracking.csv
    └── workflow_summary.json        # Processing summary
```

## Output Format

### Results JSON

```json
{
  "video_info": {
    "filename": "match.mp4",
    "status": "completed",
    "timestamp": "2024-12-15T14:30:00"
  },
  "configuration": {
    "analyzer": { ... },
    "homography": { ... },
    "player_analysis": { ... },
    "ball_analysis": { ... }
  },
  "analysis_results": {
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

### Workflow Summary JSON

```json
{
  "timestamp": "2024-12-15T14:30:00",
  "videos_processed": 3,
  "results": [
    {
      "video": "match1.mp4",
      "status": "success",
      "output_dir": "output/analysis_20241215_143000"
    },
    {
      "video": "match2.mp4",
      "status": "success",
      "output_dir": "output/analysis_20241215_143000"
    }
  ]
}
```

## Integration Examples

### Python Script Integration

```python
import subprocess
import json
from pathlib import Path

def process_videos(video_dir, output_dir):
    """Process videos using the workflow script"""
    
    # Run workflow
    result = subprocess.run([
        'python', 'workflow.py',
        '--fragments', video_dir,
        '--output', output_dir
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        # Find the summary file
        output_path = Path(output_dir)
        summaries = list(output_path.glob('*/workflow_summary.json'))
        
        if summaries:
            with open(summaries[0]) as f:
                summary = json.load(f)
                print(f"Processed {summary['videos_processed']} videos")
                return summary
    else:
        print(f"Error: {result.stderr}")
        return None

# Usage
summary = process_videos('my_videos', 'my_results')
```

### Bash Script Integration

```bash
#!/bin/bash

# Automated nightly processing
VIDEO_DIR="/path/to/daily/footage"
OUTPUT_DIR="/path/to/results"

echo "Starting video analysis workflow..."
python workflow.py --fragments "$VIDEO_DIR" --output "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    echo "✅ Workflow completed successfully"
    
    # Optional: Archive processed videos
    timestamp=$(date +%Y%m%d)
    mkdir -p "$VIDEO_DIR/archive/$timestamp"
    mv "$VIDEO_DIR"/*.mp4 "$VIDEO_DIR/archive/$timestamp/"
    
    echo "✅ Videos archived"
else
    echo "❌ Workflow failed"
    exit 1
fi
```

## Advanced Usage

### Custom Configuration

Modify `app/config.py` before running the workflow to customize analysis parameters:

```python
# Example: Adjust detection thresholds
PLAYER_ANALYSIS_CONFIG = {
    "confidence_threshold": 0.20,  # Lower = more detections
}

BALL_ANALYSIS_CONFIG = {
    "confidence_threshold": 0.25,  # Adjust for your footage
}
```

### Filtering Videos

Pre-filter videos before processing:

```bash
#!/bin/bash

# Process only videos longer than 5 minutes
for video in fragments/*.mp4; do
    duration=$(ffprobe -v error -show_entries format=duration \
               -of default=noprint_wrappers=1:nokey=1 "$video")
    
    if (( $(echo "$duration > 300" | bc -l) )); then
        echo "Processing $video (${duration}s)"
        python workflow.py --fragments "$(dirname "$video")" \
                          --output results_filtered
    fi
done
```

### Parallel Processing

Process multiple video sets in parallel:

```bash
#!/bin/bash

# Process multiple directories simultaneously
for dir in match1 match2 match3; do
    (
        echo "Processing $dir"
        python workflow.py --fragments "$dir" --output "results_$dir"
    ) &
done

wait
echo "All processing complete"
```

## Best Practices

### 1. Organize Input Videos

```
fragments/
├── 2024-12-15/
│   ├── match_001.mp4
│   ├── match_002.mp4
│   └── match_003.mp4
└── 2024-12-16/
    ├── match_004.mp4
    └── match_005.mp4
```

Process by date:
```bash
python workflow.py --fragments fragments/2024-12-15 --output results/2024-12-15
```

### 2. Monitor Resource Usage

```bash
# Run with lower priority to avoid system slowdown
nice -n 10 python workflow.py
```

### 3. Log Processing

```bash
# Save logs for debugging
python workflow.py 2>&1 | tee workflow_$(date +%Y%m%d_%H%M%S).log
```

### 4. Error Handling

```bash
#!/bin/bash

# Retry on failure
MAX_RETRIES=3
RETRY_COUNT=0

until python workflow.py || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo "Retry $RETRY_COUNT/$MAX_RETRIES"
    sleep 10
done
```

## Troubleshooting

### Issue: No Videos Found

**Symptoms**: "No video files found" message

**Solution**:
- Check that videos are in the correct directory
- Ensure video files have supported extensions (.mp4, .mov, .avi, .mkv)
- Verify file permissions

### Issue: Processing Fails

**Symptoms**: Workflow exits with error

**Solution**:
- Check video file integrity: `ffmpeg -v error -i video.mp4 -f null -`
- Ensure sufficient disk space for output
- Review error message for specific issues

### Issue: Slow Processing

**Symptoms**: Each video takes very long to process

**Solution**:
- Use GPU-enabled hardware if available
- Process shorter video segments
- Reduce video resolution before processing
- Close other applications

### Issue: Mock Analysis Results

**Symptoms**: Results contain "mock data" note

**Explanation**: Compiled analysis modules (.pyd files) are not available

**Solutions**:
- This is expected if running on non-Windows or without compiled modules
- Use `--real` flag to attempt real analysis
- For production use, ensure compiled modules are available
- Mock data is useful for testing the workflow

## Performance Tips

### 1. Optimize Video Files

```bash
# Reduce video size before processing
ffmpeg -i input.mp4 -vcodec h264 -crf 23 -preset medium output.mp4
```

### 2. Process in Chunks

For very large video collections, process in smaller batches:

```bash
# Process 10 videos at a time
find fragments -name "*.mp4" | head -10 | while read video; do
    python workflow.py --fragments "$(dirname "$video")"
done
```

### 3. Use SSD Storage

Store input videos and output results on SSD drives for faster I/O.

## Automation Examples

### Cron Job (Linux/Mac)

```cron
# Process videos daily at 2 AM
0 2 * * * cd /path/to/footydj && python workflow.py --fragments daily_footage
```

### Windows Task Scheduler

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute 'python' `
    -Argument 'workflow.py --fragments C:\footage' `
    -WorkingDirectory 'C:\footydj'

$trigger = New-ScheduledTaskTrigger -Daily -At 2am

Register-ScheduledTask -Action $action -Trigger $trigger `
    -TaskName "FootyDJ Workflow" -Description "Daily video processing"
```

## Understanding Output Files

### Annotated Video Output

The workflow generates annotated videos with visual overlays showing analysis results.

**Video Specifications:**
- Same resolution and FPS as input video
- Format: MP4 with automatic codec selection (MPEG-4, H.264, or XVID)
- Size: Similar to original (slight increase due to overlays)

**Visual Overlays Include:**

1. **Analysis Info Panel** (top-left, semi-transparent):
   - Field detection status and confidence
   - Player count and team information
   - Ball tracking status and confidence
   - Calibration quality indicator

2. **Player Detection Boxes**:
   - Green bounding boxes around detected players
   - Player labels (P1, P2, P3, etc.)
   - Updates every 30 frames

3. **Ball Position Marker**:
   - Red circle marking ball position
   - White outline for visibility
   - Shown when ball is detected

4. **Frame Counter** (bottom):
   - Current frame / total frames

**Example Output Structure:**
```
output/analysis_20251215_142210/
├── video_name_annotated.mp4    # Annotated video output
├── video_name_results.json     # Complete analysis data
├── video_name_tracking.csv     # Frame tracking data
└── workflow_summary.json       # Processing summary
```

### JSON Results Structure

The `*_results.json` file contains:
- **timestamp**: Analysis date/time
- **video_info**: Resolution, FPS, frame count, duration
- **analysis_results**: 
  - field_detection: Lines detected, confidence
  - player_tracking: Player counts, team info
  - ball_tracking: Detection status, confidence
  - homography: Calibration quality
- **configuration**: Analysis parameters used

### CSV Tracking Data

The `*_tracking.csv` file provides frame-by-frame data:
- Frame number
- Players detected per frame
- Ball detection status per frame

## Getting Help

- See [User Guide](USER_GUIDE.md) for general usage
- Check [API Documentation](API.md) for integration details
- Review [Setup Guide](SETUP.md) for installation issues

---

**Happy Processing! ⚽**
