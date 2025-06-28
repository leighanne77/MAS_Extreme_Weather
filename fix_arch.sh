#!/bin/bash

echo "🔧 Fixing Tool Architecture Issues..."
echo "======================================"

# Check current architecture
echo "Current architecture: $(uname -m)"
echo "Python architecture: $(python -c "import platform; print(platform.machine())")"

# Remove problematic packages
echo ""
echo "Removing old packages..."
pip uninstall -y pydantic fastapi uvicorn jinja2 python-multipart 2>/dev/null || true

# Clear cache
echo "Clearing pip cache..."
pip cache purge

# Reinstall with correct architecture
echo "Reinstalling packages..."
pip install --force-reinstall --no-cache-dir fastapi uvicorn jinja2 python-multipart

# Test installation
echo ""
echo "Testing installation..."
if python -c "import fastapi, uvicorn, jinja2; print('✅ All packages working!')" 2>/dev/null; then
    echo "✅ Architecture issue fixed!"
    echo ""
    echo "🎉 Success! You can now run the Tool system:"
    echo "   python demo.py"
    echo "   python simple_example.py"
    echo "   python src/tool_web/interface.py"
else
    echo "❌ Still having issues. Try the virtual environment approach:"
    echo "   python -m venv tool_env"
    echo "   source tool_env/bin/activate"
    echo "   pip install fastapi uvicorn jinja2 python-multipart"
fi 