# Architecture Overview

## Development Philosophy
The system should be:
- **Local-first:** Prioritize local computation
- **Modular:** Components must be replaceable
- **Hardware-independent:** Work across Windows, Raspberry Pi, mini PC
- **Model-independent:** Support multiple LLMs
- **Expandable:** Easy to add new capabilities

## High-Level Architecture

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
          (Fallback)      (Optional)
              |               |
              +-------+-------+
                      |
            Memory + Personality
                      |
            Response Engine
                      |
                    Teddy
```

## Component Layers

### 1. Voice Pipeline
```
Microphone
    ↓
Speech-to-Text (STT)
    ↓
Text Processing
    ↓
LLM Processing
    ↓
Text-to-Speech (TTS)
    ↓
Speaker
```

### 2. AI Router
Routes requests to appropriate models based on:
- Request type (story, conversation, educational, complex reasoning)
- Model availability (local vs. cloud)
- Performance requirements
- Resource constraints

### 3. Memory System
- **Short-term:** Current conversation context
- **Long-term:** Persistent preferences and interaction history
- **Dynamic Retrieval:** Only relevant memories added to prompts

### 4. Personality System
Separate from LLM core:
```
Teddy Personality
    +
Child Profile
    +
Relevant Memories
    +
Current Request
    = Constructed Prompt
```

## Current Hardware Architecture

### Windows 11 Machine
- Local LLM execution (Ollama or equivalent)
- Development environment
- Model testing and benchmarking
- Voice processing

### Raspberry Pi (Development Server)
- Git server (Gitea)
- Project documentation
- Configuration management
- Lightweight database
- API gateway
- Remote access (Tailscale)

### Future: Mini PC
64GB+ RAM, 2TB NVMe for dedicated AI workstation with optional external GPU via OCuLink/USB4

## Physical Teddy Architecture (Future)
```
Teddy Bear
    |
    +-- Microphone
    +-- Speaker
    +-- Wi-Fi
    +-- Lightweight Controller
          |
       Home Network
          |
    Home AI Server
    +-- LLM
    +-- Memory
    +-- Voice Processing
    +-- Personality Engine
```
Teddy acts as interface; heavy processing on home server.

## Model Support Strategy

### Supported LLMs
- Qwen family
- Llama family
- Gemma family
- Future models (architecture allows addition)

### Cloud Integration
- Optional, not required
- Fallback for difficult queries
- Fully configurable

## Data Flow (MVP)

```
User Voice Input
    ↓
STT (Whisper/Alternative)
    ↓
Extract Intent & Context
    ↓
Load Relevant Memories
    ↓
Construct Prompt with Personality
    ↓
Local LLM (Qwen/Llama/Gemma)
    ↓
Post-process Response
    ↓
TTS (Piper/Alternative)
    ↓
Audio Output to Speaker
```

## Modularity & Replaceable Components

| Layer | Current | Alternative 1 | Alternative 2 |
|-------|---------|---|---|
| STT | Whisper | Vosk | Cloud STT |
| LLM | Qwen 7B | Llama 2 7B | Gemma 7B |
| TTS | Piper | Bark | Cloud TTS |
| Memory | SQLite | PostgreSQL | Vector DB |
| Inference | Ollama | vLLM | LM Studio |

The application core remains unchanged when swapping components.

## Security & Privacy
- Local-first processing minimizes data leaving home
- Memory stored locally by default
- Cloud integration requires explicit opt-in
- No personal data sent to external services unless configured

## Scalability Path
1. Single machine (Windows 11)
2. Distributed (Windows + Raspberry Pi)
3. Dedicated mini PC with GPU
4. Multiple model servers
5. Embedded in physical Teddy
