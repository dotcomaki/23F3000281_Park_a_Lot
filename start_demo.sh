#!/bin/bash

# Parking App Demo Setup Script
# This script sets up the parking app for demo by creating a virtual environment,
# installing dependencies, and setting up the admin user.

set -e  # Exit on any error

echo "Setting up Parking App for Demo..."
echo "=================================="

# Get the script directory to ensure we're in the right location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Node.js and npm are available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in PATH"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed or not in PATH"
    exit 1
fi

echo "Python version: $(python3 --version)"
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip to latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
    echo "Requirements installed successfully"
else
    echo "Error: backend/requirements.txt not found"
    exit 1
fi

# Set up the database and create admin user
echo "Setting up database and creating admin user..."
if [ -f "backend/create_admin.py" ]; then
    # Set PYTHONPATH to include project root so backend package can be imported
    export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
    python3 backend/create_admin.py
    echo "Database and admin user setup complete"
else
    echo "Error: backend/create_admin.py not found"
    exit 1
fi

# Install frontend dependencies
echo "Installing frontend dependencies..."
if [ -f "frontend/package.json" ]; then
    cd frontend
    npm install
    cd ..
    echo "Frontend dependencies installed successfully"
else
    echo "Error: frontend/package.json not found"
    exit 1
fi

echo ""
echo "🎉 Demo setup complete!"
echo "======================"
echo ""