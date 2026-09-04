# Teddy AI - Local-First AI Companion for Children

🧸 **Build an AI companion that grows with your child over many years**

This is a local-first AI companion project designed to provide personalized, voice-based interaction with consistent personality and long-term memory. Eventually, the AI will be embodied in a physical Teddy Bear.

## Project Vision

Create a private, personalized AI companion that:
- Speaks naturally to children
- Remembers preferences and interactions
- Adapts language to the child's age
- Becomes a long-term friend
- Respects privacy (local processing first)
- Remains flexible to adopt better AI models over time

## Current Status: Phase 1 (MVP Development)

**Goal:** A user can speak to Teddy and receive a spoken AI response from a local LLM

✅ Project structure and documentation complete  
✅ Core module architecture defined  
✓ Configuration framework ready  
⏳ Full dependency installation and testing  
⏳ LLM integration (Ollama)  
⏳ Speech pipeline (STT + TTS)  

## Quick Start

### Prerequisites
- Python 3.9+
- Ollama ([Install here](https://ollama.ai)) - for local LLM
- ~4GB disk space
- macOS, Linux, or Windows

### Setup (30 seconds)

```bash
# Clone the repository
git clone https://github.com/ambujmaurya007/USSOregon.git
cd USSOregon

# Run setup script
bash scripts/setup_dev.sh

# Start Ollama (in another terminal)
ollama serve

# Pull a model
ollama pull qwen:7b

# Test the system
source venv/bin/activate
python scripts/cli.py status
python scripts/cli.py test memory
```

### First Demo

```bash
python scripts/cli.py demo --mode text
```

Type messages to Teddy and see responses!

## Architecture

```
                     User
                      |
              Voice Input/Output
                      |
        +-------------+-------------+
        |             |             |
     Speech-to-Text   AI Router   Text-to-Speech
        |             |             |
        +-----+-------+-------+-----+
              |               |
          Local LLM       Cloud LLM
          (Ollama)        (Optional)
              |               |
              +-------+-------+
                      |
            Memory + Personality
                      |
                    Teddy
```

## Project Structure

```
USSOregon/
├── README.md                    # This file
├── docs/                        # Documentation
│   ├── VISION.md               # Project vision and goals
│   ├── ARCHITECTURE.md         # Technical architecture
│   ├── ROADMAP.md              # Development roadmap
│   ├── DECISIONS.md            # Architecture decisions (ADRs)
│   └── SETUP.md                # Detailed setup guide
├── config/                      # Configuration files
│   ├── teddy.yaml              # Main configuration
│   └── .env.example            # Environment variables template
├── ai/                          # AI/LLM modules
│   ├── llm_router/             # LLM provider interface
│   ├── providers/              # Specific LLM implementations
│   ├── prompts/                # Prompt templates
│   └── benchmark/              # Model benchmarking
├── voice/                       # Voice processing
│   ├── stt/                    # Speech-to-Text
│   └── tts/                    # Text-to-Speech
├── memory/                      # Memory systems
│   ├── short_term/             # Conversation context
│   └── long_term/              # Persistent memory
├── personality/                 # Personality system
│   ├── personality_engine.py   # Personality management
│   └── teddy_default.yaml      # Default personality config
├── backend/                     # Backend services
│   ├── api/                    # REST API (future)
│   ├── services/               # Core services
│   └── models/                 # Data models
├── scripts/                     # Development scripts
│   ├── setup_dev.sh            # Development environment setup
│   ├── setup_raspberry_pi.sh   # Raspberry Pi setup
│   └── cli.py                  # CLI tool
├── tests/                       # Unit and integration tests
├── android/                     # Android app (future)
├── teddy/                       # Physical Teddy (future)
├── requirements.txt             # Python dependencies
└── .gitignore                  # Git ignore rules
```

## Key Features (MVP)

### ✅ Implemented
- Modular component architecture
- Configuration-driven behavior
- SQLite memory backend
- Personality engine with age-appropriate responses
- LLM provider abstraction
- Speech pipeline scaffolding

### 🔄 In Progress
- Ollama integration
- Whisper speech-to-text
- Piper text-to-speech
- End-to-end voice pipeline

### 🚀 Coming Soon
- Multi-model routing
- Mobile interface
- Physical Teddy integration
- Benchmark framework

## Development Roadmap

| Phase | Focus | Timeline |
|-------|-------|----------|
| 1 | Voice pipeline MVP | 4-6 weeks |
| 2 | Personality & Memory | 3-4 weeks |
| 3 | Multi-model Router | 3-4 weeks |
| 4 | Mobile Interface | 6-8 weeks |
| 5 | Physical Teddy | 8-12 weeks |

## Documentation

- **[VISION.md](docs/VISION.md)** — Project vision and product concept
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Technical architecture and components
- **[ROADMAP.md](docs/ROADMAP.md)** — Detailed development roadmap with phases
- **[DECISIONS.md](docs/DECISIONS.md)** — Architecture decision records (ADRs)
- **[SETUP.md](docs/SETUP.md)** — Detailed setup instructions

## Development Principles

### Local-First
All processing happens locally by default. Cloud services are optional and must be explicitly configured.

### Modular
Every major component has a pluggable interface. Swap LLMs, STT engines, and TTS engines without rewriting the app.

### Hardware-Independent
Software works on Windows, Raspberry Pi, and future mini PCs. Hardware changes don't require code changes.

### Model-Agnostic
Support multiple LLM families (Qwen, Llama, Gemma) with a provider abstraction layer.

## Hardware Setup

### Current
- **Windows 11 PC:** Local LLM execution (Ollama)
- **Raspberry Pi:** Development infrastructure (Git, docs, config, optional DB)

### Future
- **Mini PC:** Dedicated AI workstation with optional GPU

## Contributing

1. Read the architecture documentation
2. Follow the existing code structure
3. Add tests for new components
4. Update documentation
5. Use feature branches
6. Create pull requests with clear descriptions

## Privacy & Data

- No data sent to cloud by default
- All personal interactions stored locally
- Memory remains on home network
- Cloud integration is opt-in only

## License

[To be determined]

## Support

- 📖 Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details
- 🐛 Check [GitHub Issues](https://github.com/ambujmaurya007/USSOregon/issues)
- 💬 Start a discussion for questions

## Next Steps

1. ✅ Project structure created
2. Next: Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Next: Set up Ollama with a model
4. Next: Run integration tests
5. Next: Build voice pipeline

---

**Built with ❤️ for growing up together**