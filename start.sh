#!/bin/bash
echo "=========================================="
echo "  CodeForge - Teacher PC Launcher"
echo "=========================================="
echo ""

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "Install: sudo apt install python3 python3-pip"
    exit 1
fi

# Install dependencies if needed
if [ ! -f "server/.deps_installed" ]; then
    echo "[1/3] Installing Python dependencies..."
    pip3 install -r server/requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies."
        exit 1
    fi
    echo "done" > server/.deps_installed
else
    echo "[1/3] Dependencies already installed."
fi

# Set environment defaults
export AI_PROVIDER="${AI_PROVIDER:-groq}"
export TEACHER_IP="${TEACHER_IP:-192.168.1.1}"

echo ""
echo "[2/3] Configuration:"
echo "  AI Provider: $AI_PROVIDER"
echo "  Teacher IP:  $TEACHER_IP"
echo ""

echo "[3/3] Starting CodeForge server on port 8000..."
echo "Dashboard URL: http://localhost:5173"
echo "API docs:      http://192.168.1.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop."
echo ""

python3 -m uvicorn server.main:app --host 0.0.0.0 --port 8000
