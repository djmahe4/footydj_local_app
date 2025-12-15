# GitHub Actions Workflows

This directory contains automated workflows for testing and validating the FootyDJ application.

## Test Video Analysis Workflow

**File:** `test-video-analysis.yml`

This workflow automatically tests the video analysis functionality using the test video in the `fragments/` directory.

### Triggers

- Push to `master` or `develop` branches
- Pull requests to `master` or `develop` branches
- Manual trigger via GitHub Actions UI

### What It Does

1. **Setup Environment** - Installs Python 3.11 and dependencies
2. **Video Verification** - Confirms test video exists
3. **License Testing** - Tests license activation if secret is configured
4. **Workflow Execution** - Runs the video analysis workflow
5. **Output Validation** - Verifies all expected output files are generated
6. **JSON Validation** - Checks the structure of analysis results
7. **Artifact Upload** - Saves output files as workflow artifacts

### License Testing

The workflow includes license activation testing using securely configured credentials.

### Expected Output

The workflow creates the following files:

- `*_annotated.mp4` - Video with analysis overlays
- `*_results.json` - Complete analysis results
- `*_tracking.csv` - Frame-by-frame tracking data
- `workflow_summary.json` - Processing summary

These files are uploaded as artifacts and retained for 7 days.

### Viewing Results

1. Go to **Actions** tab in your repository
2. Click on a workflow run
3. Scroll to **Artifacts** section at the bottom
4. Download `analysis-output` to view generated files

### Troubleshooting

**Workflow fails with "Error: Test video not found"**
- Ensure `fragments/1743634379_000002.mp4` exists in the repository
- Check that the video file isn't ignored by `.gitignore`

**Codec errors in video generation**
- The workflow tries multiple video codecs (MPEG-4, H.264, XVID)
- If all fail, check OpenCV installation in the workflow

**License test skipped**
- This is normal if `FOOTYDJ_LICENSE_KEY` secret isn't configured
- The workflow will still test video analysis functionality

### Manual Trigger

You can manually trigger this workflow:

1. Go to **Actions** tab
2. Select **Test Video Analysis** workflow
3. Click **Run workflow**
4. Choose the branch
5. Click **Run workflow** button

## Future Workflows

Additional workflows can be added for:
- Code compilation and build testing
- Security scanning
- Documentation deployment
- Release automation
