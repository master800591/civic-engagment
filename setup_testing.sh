#!/bin/bash

# Setup script for Civic Engagement Platform CI/Testing

echo "🏗️ Setting up Civic Engagement Platform for CI Testing"
echo "======================================================"

# Change to the civic_desktop directory
cd civic_desktop

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Make sure you're in the project root."
    exit 1
fi

echo "📍 Current directory: $(pwd)"

# Update pip
echo "📦 Updating pip..."
python -m pip install --upgrade pip

# Install main dependencies
echo "📦 Installing main dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install -r requirements-dev.txt

# Install additional testing tools
echo "🔧 Installing additional testing tools..."
pip install pytest-timeout pytest-mock pytest-html

# Clean cache files
echo "🧹 Cleaning cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f -delete 2>/dev/null || true

# Test basic imports
echo "🔍 Testing basic imports..."
python -c "import main; print('✅ Main module imports successfully')" || echo "❌ Main import failed"
python -c "import users.backend; print('✅ Users backend imports successfully')" || echo "❌ Users backend import failed"

# Test basic module compilation
echo "🔍 Testing module compilation..."
python -m py_compile main.py && echo "✅ main.py compiles successfully" || echo "❌ main.py compilation failed"

# Run syntax check on test files
echo "🔍 Checking test file syntax..."
for test_file in tests/*.py tests/*/*.py; do
    if [ -f "$test_file" ]; then
        if python -m py_compile "$test_file"; then
            echo "✅ $test_file syntax OK"
        else
            echo "❌ $test_file syntax error"
        fi
    fi
done

# Check if tests can be collected
echo "🔍 Testing pytest collection..."
if python -m pytest tests/ --collect-only -q > /dev/null 2>&1; then
    echo "✅ Test collection successful"
    TEST_COUNT=$(python -m pytest tests/ --collect-only -q 2>/dev/null | wc -l)
    echo "📊 Found $TEST_COUNT tests"
else
    echo "❌ Test collection failed"
fi

# Run security checks
echo "🔒 Running security checks..."
if command -v bandit &> /dev/null; then
    echo "🔍 Running Bandit security scan..."
    bandit -r . --severity-level medium -f txt || echo "⚠️ Bandit found security issues"
else
    echo "⚠️ Bandit not installed, skipping security scan"
fi

# Check for secrets
echo "🔍 Checking for accidentally committed secrets..."
if find . -name "*.pem" -o -name "*.key" -o -name "*.p12" | grep -v /tmp/ | grep -v test | head -5; then
    echo "⚠️ Found potential private key files (review these)"
else
    echo "✅ No obvious private key files found"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   • Run tests: python -m pytest tests/ -v"
echo "   • Run with coverage: python -m pytest tests/ --cov=."
echo "   • Run security scan: bandit -r ."
echo "   • Start application: python main.py"
echo ""
echo "🔧 Troubleshooting:"
echo "   • If PyQt5 issues on Linux: sudo apt-get install python3-pyqt5"
echo "   • If GUI tests fail: use xvfb-run python -m pytest tests/"
echo "   • Check config: verify config/*.json files exist"
echo ""