"""
Main entry point for FootyDJ Local Application
Launches the web interface in a desktop window using pywebview
"""

import os
import sys
import threading
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    print("Warning: pywebview not installed. Running in browser-only mode.")

from app.server import start_server
from app.config import APP_CONFIG


def start_backend():
    """Start the FastAPI backend server in a separate thread"""
    host = APP_CONFIG.get("host", "127.0.0.1")
    port = APP_CONFIG.get("port", 8000)
    start_server(host=host, port=port)


def main():
    """Main application entry point"""
    host = APP_CONFIG.get("host", "127.0.0.1")
    port = APP_CONFIG.get("port", 8000)
    url = f"http://{host}:{port}"
    
    print("=" * 60)
    print("FootyDJ Local Application")
    print("=" * 60)
    
    # Start backend server in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait for server to start
    print(f"Starting server at {url}...")
    time.sleep(2)
    
    if WEBVIEW_AVAILABLE:
        # Create desktop window with pywebview
        print("Opening desktop application window...")
        window = webview.create_window(
            title="FootyDJ Local",
            url=url,
            width=1200,
            height=800,
            resizable=True,
            fullscreen=False
        )
        webview.start()
    else:
        # Fallback: just run the server
        print(f"\nApplication running at: {url}")
        print("Open this URL in your web browser.")
        print("Press Ctrl+C to stop the server.")
        print("-" * 60)
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            sys.exit(0)


if __name__ == "__main__":
    main()
