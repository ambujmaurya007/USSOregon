#!/bin/bash
# Setup script for Teddy AI development environment

set -e

echo "🧸 Setting up Teddy AI Development Environment..."
echo ""

# Create necessary directories
echo "📁 Creating data directory..."
mkdir -p data logs

# Check Python version
echo "🐍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Teddy AI Environment Variables
export TEDDY_CONFIG="config/teddy.yaml"
export TEDDY_DB_PATH="./data/teddy.db"
export LOG_LEVEL="INFO"

# Optional: Cloud LLM configuration
# export OPENAI_API_KEY="your-key-here"
# export ANTHROPIC_API_KEY="your-key-here"
EOF
    echo "  .env file created. Please edit with your settings."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure Ollama is running: ollama serve"
echo "2. Pull a model: ollama pull qwen:7b"
echo "3. Activate virtual environment: source venv/bin/activate"
echo "4. Run the service: python backend/services/teddy_service.py"
echo ""
echo "For more information, see: docs/SETUP.md"
