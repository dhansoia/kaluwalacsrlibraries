#!/bin/bash
# Kaluwala CSR Libraries - Mac/Linux Setup Script
# Save this as setup.sh and run with: bash setup.sh

echo "====================================="
echo "Kaluwala CSR Libraries Network Setup"
echo "====================================="
echo ""

# Check Python installation
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ $PYTHON_VERSION"
else
    echo "✗ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -eq 0 ]; then
    echo "✓ Virtual environment created"
else
    echo "✗ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Create instance directory
echo ""
echo "Creating instance directory..."
mkdir -p instance
echo "✓ Instance directory ready"

echo ""
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo ""
echo "To start the application:"
echo "  source venv/bin/activate  # Activate virtual environment"
echo "  python app.py             # Start the server"
echo ""
echo "Then visit: http://localhost:5000"
echo ""
