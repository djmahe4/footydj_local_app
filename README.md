# FootyDJ Local Application

This directory contains a locally deployable version of the FootyDJ video analysis tool, packaged as a hybrid desktop application.

## Architecture

This application uses a hybrid architecture to provide a modern user interface while running entirely on the user's machine.

-   **Backend**: A lightweight [FastAPI](https://fastapi.tiangolo.com/) server runs locally to handle API requests and perform the heavy video processing.
-   **Frontend**: The UI is built with standard HTML, CSS, and JavaScript.
-   **Wrapper**: [PyWebView](https://pywebview.flowrl.com/) is used to create a native OS window that displays the frontend and runs the backend server in the background.
-   **Distribution**: [PyInstaller](https://pyinstaller.org/) is used to package the entire application (Python, server, UI, and models) into a single executable file.

## Security & Licensing

This application includes a commercial licensing and IP protection mechanism.

1.  **Code Protection**: Sensitive Python modules (`licensing.py`, `security.py`) are compiled into native C extensions using [Cython](https://cython.org/). This makes reverse-engineering the core licensing and security logic extremely difficult.
2.  **Model Protection**: The YOLO models are scrambled using a secret key before being bundled. The application unscrambles the model in memory at runtime, so the usable model file never touches the disk. The scrambling key is stored in a Cython-compiled module.
3.  **Subscription Model**: A hybrid online/offline licensing model is used:
    -   A license key is validated against a simple, low-cost serverless function.
    -   On successful validation, a signed, time-limited (e.g., 7 days) activation token is stored locally.
    -   The application can run completely offline as long as the token is valid.
    -   It only requires an internet connection to re-activate the token once it expires.

## Quick Start

### For Users

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   python build_tools/init_models.py
   ```

2. **Run the application:**
   ```bash
   # Desktop application
   python app/main.py
   
   # Or batch processing
   python workflow.py
   ```

3. **Open in browser:**
   Navigate to `http://127.0.0.1:8000`

See the [Setup Guide](docs/SETUP.md) for detailed installation instructions.

### For Developers/Production

See [PRODUCTION.md](PRODUCTION.md) for:
- Compiling code with Cython
- Encrypting models
- Building executables
- Production deployment

## Documentation

Complete documentation is available in the `docs/` directory:

- **[Setup Guide](docs/SETUP.md)** - Installation and configuration
- **[User Guide](docs/USER_GUIDE.md)** - How to use the application
- **[Workflow Guide](docs/WORKFLOW_GUIDE.md)** - Batch video processing
- **[API Documentation](docs/API.md)** - REST API reference
- **[Production Guide](PRODUCTION.md)** - Deployment and compilation

## Testing

The repository includes automated testing via GitHub Actions:
- Video analysis workflow testing
- Output validation
- JSON structure verification

See `.github/workflows/` for workflow definitions.

## Features

- **Field Detection**: Automatically identifies football field lines and boundaries
- **Player Tracking**: Tracks player positions and movements across frames
- **Ball Tracking**: Follows ball trajectory and analyzes possession
- **Camera Calibration**: Transforms video coordinates to real-world field positions
- **Batch Processing**: Process multiple videos automatically with `workflow.py`
- **Web Interface**: Modern, responsive UI for easy interaction
- **REST API**: Programmable interface for integration

## System Requirements

- **Python**: 3.11.x (compiled modules built for Python 3.11)
- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 5GB free space for models and output
- **GPU**: Optional but recommended (CUDA-compatible NVIDIA GPU)

## License

This software requires a valid license key to operate. Contact FootyDJ for licensing information.
