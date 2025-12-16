# Production Deployment Guide

This guide covers the complete process for preparing and deploying the FootyDJ application for production use.

## Prerequisites

- Windows 10/11 (64-bit) with Python 3.11.x
- All dependencies installed (`pip install -r requirements.txt`)
- Cython compiler available
- Access to the codebase and models

## Production Build Steps

### 1. Compile Python Source Code

The application uses Cython to compile Python modules into native extensions (.pyd files) for IP protection and performance.

**Compile all modules:**

```bash
# From repository root
python build_tools/setup.py build_ext --inplace
```

This will compile:
- `app/main.py` → `app/main.cp311-win_amd64.pyd`
- `app/server.py` → `app/server.cp311-win_amd64.pyd`
- All other Python files in `app/` directory (excluding `__init__.py` and `config.py`)

**Verify compilation:**

```bash
# Check that .pyd files were created
ls app/*.pyd
ls app/footydj5/*/*.pyd
```

### 2. Model Protection

Scramble the YOLO models before distribution:

```bash
python build_tools/encrypt_model.py
```

This creates encrypted versions of models that can only be used by the application.

### 3. Clean Source Files (Production Only)

**IMPORTANT:** Only do this for final production distribution, not during development.

For production deployment, you can remove the Python source files since the compiled .pyd files contain the code:

```bash
# Backup first!
# Remove .py source files (keep config.py and __init__.py)
find app -name "*.py" ! -name "__init__.py" ! -name "config.py" -type f -delete
```

**Keep these files:**
- `app/config.py` - Configuration (users may need to modify)
- All `__init__.py` files - Required for Python module structure
- `workflow.py` - User-facing script

### 4. Build Executable (Optional)

To create a standalone executable:

```bash
pyinstaller main.spec
```

This packages everything into a single .exe file in the `dist/` folder.

## Production Deployment Checklist

### Code Preparation
- [x] All Python modules compiled to .pyd files
- [x] Models encrypted/scrambled
- [x] Source .py files removed (except config.py, __init__.py, and workflow.py)
- [x] Compiled modules tested and working

### Security
- [x] License validation implemented
- [x] Sensitive code in compiled modules
- [x] No hardcoded credentials in code
- [x] Models protected from extraction

### Testing
- [x] Video analysis workflow tested
- [x] Web interface functional
- [x] API endpoints working
- [x] License activation tested
- [x] All output files generated correctly

### Documentation
- [x] User documentation complete
- [x] API documentation available
- [x] Installation instructions clear
- [x] Troubleshooting guide provided

### Distribution
- [x] Requirements.txt up to date
- [x] All dependencies documented
- [x] Models downloadable or included
- [x] License terms clear

## File Structure (Production)

```
footydj_local_app/
├── app/
│   ├── config.py                      # User-configurable settings
│   ├── *.pyd                          # Compiled modules (NOT .py)
│   ├── footydj5/
│   │   └── */*.pyd                    # Compiled analysis modules
│   └── encrypted_models/              # Protected model files
│
├── frontend/                          # Web interface
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── fragments/                         # Input video directory
├── models/                            # YOLO models (encrypted)
├── workflow.py                        # User-facing batch script
├── requirements.txt                   # Dependencies
└── README.md                          # User documentation
```

## What NOT to Include in Production

Remove these development files:
- `*.py` files in `app/` (except config.py, __init__.py)
- `build_tools/` directory (only needed for compilation)
- `.git/` directory
- Test output directories
- Development documentation (IMPLEMENTATION_SUMMARY.md, etc.)

## Running in Production

Users run the application with:

```bash
# Desktop application (recommended)
python app/main.py

# Or server only
python app/server.py

# Or batch processing
python workflow.py
```

The application will import from compiled .pyd modules automatically.

## Important Notes

### Platform Compatibility

- `.pyd` files are platform-specific (Windows Python 3.11 x64)
- For other platforms, either:
  - Recompile on target platform
  - Distribute source `.py` files for those platforms
  - Use the workflow script which handles both scenarios

### User Modifications

Users can still modify:
- `app/config.py` - Analysis parameters
- `workflow.py` - Batch processing logic (if needed)
- Frontend files - UI customization

### Updates and Patches

For updates:
1. Update source `.py` files in development
2. Test thoroughly
3. Recompile with `setup.py build_ext --inplace`
4. Distribute new `.pyd` files to users

## Verification

After preparing for production, verify:

```bash
# 1. Check compiled modules exist
ls -lh app/*.pyd

# 2. Test import (should work without .py files)
python -c "from app import server; print('✓ Server module loads')"

# 3. Run workflow test
python workflow.py --fragments fragments --output test_output

# 4. Start web interface
python app/main.py
```

## Troubleshooting

**Error: "No module named 'app.something'"**
- Ensure all required modules are compiled
- Check that __init__.py files are present
- Verify Python version matches (3.11)

**Error: "Cannot import compiled module"**
- Check platform compatibility (Windows x64)
- Verify Python version (must be 3.11.x)
- Ensure all dependencies installed

**Models not loading**
- Run `python build_tools/init_models.py` to download
- Check models/ directory exists
- Verify model files are present

## Support

For production deployment issues, check:
1. System meets requirements (Python 3.11, Windows)
2. All dependencies installed correctly
3. Compiled modules present and not corrupted
4. Models downloaded and encrypted properly

## Security Considerations

- Never distribute unencrypted models
- Keep license validation server secure
- Monitor for unauthorized usage
- Regular security audits recommended