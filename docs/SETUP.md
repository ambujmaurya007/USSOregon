# Setup Guide for Teddy AI Development

This guide covers setting up Teddy AI on your local machine for development.

## System Requirements

- **OS:** macOS, Linux, or Windows
- **Python:** 3.9 or higher
- **RAM:** 8GB minimum (16GB+ recommended for larger models)
- **Disk Space:** 50GB+ (for models and data)
- **GPU:** Optional (CUDA or Metal for faster inference)

## Step 1: Clone Repository

```bash
git clone https://github.com/ambujmaurya007/USSOregon.git
cd USSOregon
```

## Step 2: Run Setup Script

```bash
# Make script executable
chmod +x scripts/setup_dev.sh

# Run setup
bash scripts/setup_dev.sh
```

This will:
- Create virtual environment
- Install dependencies from `requirements.txt`
- Create necessary directories (`data/`, `logs/`)
- Create `.env` configuration file

## Step 3: Install Ollama

Ollama provides local LLM inference.

### macOS
```bash
# Download from https://ollama.ai
# Or use Homebrew
brew install ollama
```

### Linux
```bash
curl https://ollama.ai/install.sh | sh
```

### Windows
Download installer from https://ollama.ai/download

## Step 4: Pull a Model

In a new terminal:

```bash
# Start Ollama server
ollama serve

# In another terminal, pull a model
ollama pull qwen:7b
```

Available models:
- `qwen:7b` - Small, fast (recommended for testing)
- `qwen:14b` - Medium, better quality
- `llama2:7b` - Alternative small model
- `llama2:13b` - Alternative medium model
- `gemma:7b` - Google Gemma model

## Step 5: Verify Installation

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Check status
python scripts/cli.py status

# Test memory backend
python scripts/cli.py test memory

# Test LLM provider
python scripts/cli.py test llm
```

## Step 6: Install Optional Dependencies

### For Speech-to-Text (Whisper)
```bash
pip install openai-whisper
# First run downloads the model (~1.4GB)
```

Whisper also requires FFmpeg to decode microphone recordings. The project installs
`imageio-ffmpeg` with the main requirements and uses its bundled executable when
FFmpeg is not already available on Windows.

### For Text-to-Speech (Piper)
```bash
pip install piper-tts
```

### For GPU Acceleration
```bash
# CUDA (NVIDIA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Metal (Apple Silicon)
pip install torch torchvision torchaudio
```

## Step 7: Configure Teddy

Edit `config/teddy.yaml` to customize:

```yaml
# Set your child's profile
child:
  name: "Your child's name"
  age: 3
  age_group: "preschool"
  language: "en"
  interests:
    - "animals"
    - "stories"

# Configure LLM
llm:
  primary_provider: "ollama"
  providers:
    ollama:
      api_url: "http://localhost:11434"
      model: "qwen:7b"
```

Gemini is optional and disabled by default. To enable it, set `GEMINI_API_KEY`
in the environment, set `llm.providers.gemini.enabled` to `true`, and enable
cloud fallback only if sending eligible requests to the cloud is acceptable:

```yaml
llm:
  providers:
    gemini:
      enabled: true
      model: "gemini-2.5-flash"
      api_key_env: "GEMINI_API_KEY"
  routing:
    default: "ollama"
    allow_cloud_fallback: true
    cloud_fallback_on_error: true
```

## Step 8: Run Demo

```bash
# Text-based demo
python scripts/cli.py demo --mode text

# Voice demo (requires Whisper + Piper)
python scripts/cli.py demo --mode voice
```

## Raspberry Pi Setup

For setting up a Raspberry Pi as infrastructure hub:

```bash
chmod +x scripts/setup_raspberry_pi.sh
bash scripts/setup_raspberry_pi.sh
```

This installs:
- Docker
- Git server (Gitea)
- SQLite with web interface
- Tailscale VPN
- Systemd service

## Troubleshooting

### Ollama Connection Error
**Problem:** "Connection refused" when trying to connect to Ollama
**Solution:** 
1. Make sure Ollama is running: `ollama serve`
2. Check URL in config: should be `http://localhost:11434`
3. On Windows, Ollama runs as a service automatically

### Model Not Found
**Problem:** "Model not found" error
**Solution:**
1. Make sure Ollama server is running
2. Pull the model: `ollama pull qwen:7b`
3. List available models: `ollama list`

### Out of Memory
**Problem:** "CUDA out of memory" or system freezes
**Solution:**
1. Use smaller model: `qwen:7b` instead of `qwen:14b`
2. Set quantization in Ollama
3. Increase system RAM or swap

### Virtual Environment Issues
**Problem:** "No module named..." after activation
**Solution:**
1. Delete venv: `rm -rf venv`
2. Recreate: `python3 -m venv venv`
3. Rerun setup: `bash scripts/setup_dev.sh`

## Performance Tips

1. **Use 7B models** for fast iteration during development
2. **Enable GPU** if available
3. **Use smaller quantized models** (7B GGUF)
4. **Cache models locally** after first download
5. **Monitor system resources** with `top` or `Activity Monitor`

## Development Workflow

```bash
# Activate environment
source venv/bin/activate

# Make code changes
# ...

# Test components
python scripts/cli.py test all

# Run demo
python scripts/cli.py demo --mode text

# Run unit tests (when available)
pytest tests/

# Check code style
black backend/ ai/ voice/ memory/ personality/
flake8 backend/ ai/ voice/ memory/ personality/
```

## Next Steps

1. ✅ Installation complete
2. Read [ARCHITECTURE.md](ARCHITECTURE.md)
3. Explore module documentation
4. Run tests and demos
5. Start implementing features
6. Create pull requests

## Getting Help

- Check existing documentation in `docs/`
- Review code comments and docstrings
- Check GitHub issues and discussions
- Read the architecture decision records in `DECISIONS.md`

---

**Ready to build Teddy! 🧸**
