# App Compilation Notes

## Important: server.py and main.py Compilation

The `server.py` and `main.py` files in this directory are meant to be compiled using Cython into `.pyd` files (similar to the other compiled modules in this directory).

### Current State

For development and testing purposes, Python source versions of these files exist:
- `server.py` - FastAPI backend server (should be compiled to `server.cp311-win_amd64.pyd`)
- `main.py` - Application entry point (should be compiled to `main.cp311-win_amd64.pyd`)

### Why Compile?

These files should be compiled for:
1. **IP Protection** - Prevent reverse engineering of server logic
2. **Performance** - Compiled Cython code runs faster
3. **Consistency** - Match the compilation approach of other modules (licensing.pyd, security.pyd, processing.pyd)

### How to Compile

Use the existing build system:

```bash
# From repository root
python build_tools/setup.py build_ext --inplace
```

This will:
1. Find all `.py` files in the `app/` directory (excluding __init__.py and config.py)
2. Compile them to `.pyd` files using Cython
3. Place the compiled files in the same directory

### Build System Configuration

The `build_tools/setup.py` already includes logic to compile these files:

```python
def find_py_files(directory):
    py_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "__init__.py" and file != "config.py":
                py_files.append(os.path.join(root, file))
    return py_files
```

### Production Deployment

For production deployment:
1. Compile all Python files in `app/` directory
2. Remove the `.py` source files, keep only `.pyd`
3. The application will import from compiled modules
4. Users cannot view or modify the server logic

### Development vs Production

**Development** (current state):
- Python source files available
- Easy to debug and modify
- No compilation required
- Suitable for testing and development

**Production** (after compilation):
- Only `.pyd` compiled files
- IP protected
- Better performance
- Cannot be easily modified or reverse-engineered

### Testing on Non-Windows Systems

The compiled `.pyd` files are Windows-specific (Python 3.11, x64). On other systems:
- Use the Python source versions for testing
- Compile on target platform if needed
- Or use the workflow script which handles both cases

### Note for Workflow Script

The `workflow.py` in the repository root should NOT be compiled as it's meant to be user-facing and modifiable. It handles both scenarios:
- When compiled modules are available, it uses them
- When not available, it runs in demonstration mode
