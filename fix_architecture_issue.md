# Fixing Tool Architecture Issues

## Problem
You're running on an ARM64 (Apple Silicon) Mac, but have x86_64 packages installed. This causes compatibility issues when trying to run the Tool system.

## Solution Options

### Option 1: Clean Reinstall (Recommended)

```bash
# 1. Remove existing packages
pip uninstall -y pydantic fastapi uvicorn

# 2. Clear pip cache
pip cache purge

# 3. Reinstall with correct architecture
pip install --force-reinstall pydantic fastapi uvicorn

# 4. Test the installation
python -c "import pydantic, fastapi, uvicorn; print('✅ All packages working!')"
```

### Option 2: Use a Virtual Environment

```bash
# 1. Create a new virtual environment
python -m venv tool_env

# 2. Activate the environment
source tool_env/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install packages in the clean environment
pip install fastapi uvicorn jinja2 python-multipart

# 5. Test the installation
python -c "import fastapi, uvicorn; print('✅ Virtual environment working!')"
```

### Option 3: Use Conda (Alternative)

```bash
# 1. Install Miniconda if you don't have it
# Download from: https://docs.conda.io/en/latest/miniconda.html

# 2. Create a new conda environment
conda create -n tool python=3.11

# 3. Activate the environment
conda activate tool

# 4. Install packages
conda install -c conda-forge fastapi uvicorn jinja2

# 5. Test the installation
python -c "import fastapi, uvicorn; print('✅ Conda environment working!')"
```

### Option 4: Minimal Installation (For Testing)

```bash
# Install only the essential packages needed to run the system
pip install --force-reinstall --no-cache-dir fastapi uvicorn jinja2 python-multipart

# Test with a simple server
python -c "
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get('/')
def read_root():
    return {'Hello': 'Tool'}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

## Verification Steps

After fixing the architecture issue:

1. **Test basic imports:**
   ```bash
   python -c "import fastapi, uvicorn, jinja2; print('✅ All imports working!')"
   ```

2. **Test the web interface:**
   ```bash
   cd src
   python -m tool_web.interface
   ```

3. **Open browser to:** `http://localhost:8000`

## Common Issues and Solutions

### Issue: "mach-o file, but is an incompatible architecture"
**Solution:** This means you have x86_64 packages on ARM64. Use Option 1 or 2 above.

### Issue: "No module named 'fastapi'"
**Solution:** The package wasn't installed correctly. Try Option 1.

### Issue: "Permission denied"
**Solution:** Use a virtual environment (Option 2) or add `--user` flag:
```bash
pip install --user fastapi uvicorn
```

### Issue: "Port already in use"
**Solution:** Use a different port:
```bash
python src/tool_web/interface.py --port 8001
```

## Quick Fix Script

Create a file called `fix_arch.sh`:

```bash
#!/bin/bash
echo "🔧 Fixing Tool Architecture Issues..."

# Remove problematic packages
echo "Removing old packages..."
pip uninstall -y pydantic fastapi uvicorn

# Clear cache
echo "Clearing pip cache..."
pip cache purge

# Reinstall with correct architecture
echo "Reinstalling packages..."
pip install --force-reinstall --no-cache-dir fastapi uvicorn jinja2 python-multipart

# Test installation
echo "Testing installation..."
python -c "import fastapi, uvicorn; print('✅ Architecture issue fixed!')"

echo "🎉 Done! Try running the system now."
```

Make it executable and run:
```bash
chmod +x fix_arch.sh
./fix_arch.sh
```

## After Fixing

Once the architecture issue is resolved:

1. **Run the demos:**
   ```bash
   python demo.py
   python simple_example.py
   ```

2. **Test the web interface:**
   ```bash
   python src/tool_web/interface.py
   ```

3. **Open browser to:** `http://localhost:8000`

## System Requirements

- **OS:** macOS 11+ (Big Sur) or later
- **Architecture:** ARM64 (Apple Silicon) or x86_64 (Intel)
- **Python:** 3.8+ (3.11 recommended)
- **RAM:** 4GB+ recommended
- **Storage:** 1GB+ free space

## Troubleshooting

If you continue to have issues:

1. **Check Python version:** `python --version`
2. **Check architecture:** `python -c "import platform; print(platform.machine())"`
3. **Check pip version:** `pip --version`
4. **Try different Python version:** Use Python 3.11 instead of 3.13
5. **Use Homebrew Python:** `brew install python@3.11`

## Success Indicators

You'll know the fix worked when:

- ✅ `python -c "import fastapi, uvicorn"` runs without errors
- ✅ The web interface starts without architecture errors
- ✅ You can access `http://localhost:8000` in your browser
- ✅ The demos run successfully

---

**Need help?** The architecture issue is common on Apple Silicon Macs. The solutions above should resolve it. 