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

## How to Run

1.  Download the models:
    ```bash
    python build_tools/init_models.py
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the main application script:
    ```bash
    python app/main.py
    ```

## How to Build

1.  (First time) Scramble the model:
    ```bash
    python build_tools/encrypt_model.py
    ```
2.  Compile the Cython modules:
    ```bash
    python build_tools/setup.py build_ext --inplace
    ```
3.  Build the executable:
    ```bash
    pyinstaller main.spec
    ```
