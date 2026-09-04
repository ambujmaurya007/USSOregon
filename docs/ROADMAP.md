# Development Roadmap

## Phase 1: MVP - Voice Pipeline (Current)
**Goal:** A user can speak to Teddy and receive a spoken AI response from a local LLM

### Deliverables
- [ ] Local LLM setup (Ollama + Qwen/Llama)
- [ ] Speech-to-Text pipeline
- [ ] Basic text-to-response
- [ ] Text-to-Speech pipeline
- [ ] Complete voice loop
- [ ] Simple CLI interface for testing

### Tasks (Priority Order)
1. Set up private Git repository structure ✓
2. Set up Raspberry Pi as development infrastructure
3. Set up local LLM on Windows 11
4. Create simple Python program: Input Text → Local LLM → Output Text
5. Add Teddy personality layer
6. Add Text-to-Speech
7. Add Speech-to-Text
8. Connect complete voice pipeline
9. Create test harness and demo

### Success Criteria
```
User Voice Input
    ↓
Microphone Capture
    ↓
STT Processing
    ↓
LLM Response (with Teddy personality)
    ↓
TTS Processing
    ↓
Speaker Output
```

**First demo:** "Hello Teddy, tell me a story about an elephant." → Teddy responds with personalized story.

---

## Phase 2: Personality & Memory System
**Goal:** Teddy remembers preferences and adapts responses

### Deliverables
- [ ] Persistent memory database (SQLite)
- [ ] Memory retrieval system
- [ ] Child profile management
- [ ] Personality prompt templates
- [ ] Memory update system (learns from interactions)
- [ ] Age-appropriate response filtering

### Key Modules
- Memory/short_term: Conversation context
- Memory/long_term: Persistent preferences
- Personality: Dynamic prompt construction
- Profile: Child information and preferences

### Success Criteria
- Teddy remembers child's name
- Teddy recalls favorite animals/colors/stories
- Teddy adapts language to child's age
- Teddy references previous interactions

---

## Phase 3: AI Router & Multi-Model Support
**Goal:** Intelligently route requests to best-available model

### Deliverables
- [ ] Model abstraction layer
- [ ] AI Router for request classification
- [ ] Model benchmark framework
- [ ] Support for Qwen, Llama, Gemma families
- [ ] Cloud LLM fallback (optional)
- [ ] Model performance tracking

### Benchmark Categories
1. Storytelling
2. Child-friendly conversation
3. Personality consistency
4. Following instructions
5. Language support (English, Hindi, etc.)
6. Reasoning capability
7. Educational explanations
8. Creativity
9. Response latency
10. Resource efficiency

### Success Criteria
- System selects optimal model per request type
- Easy to add new models
- Seamless fallback to cloud if configured
- Model performance metrics dashboard

---

## Phase 4: Mobile Interface
**Goal:** Android app for on-the-go interaction

### Deliverables
- [ ] Android UI (React Native or Flutter)
- [ ] Voice recording interface
- [ ] Response playback
- [ ] Memory visualization
- [ ] Settings and configuration
- [ ] Offline mode support

### Features
- Voice button UI
- Transcription display
- Response animation
- History view
- Preferences/settings
- Emergency shutdown

---

## Phase 5: Physical Teddy Embodiment
**Goal:** Integrate AI into physical plush toy

### Deliverables
- [ ] Teddy hardware design (microphone, speaker, controller)
- [ ] Wi-Fi communication layer
- [ ] Physical express ion (LED eyes, motion)
- [ ] Battery management
- [ ] Home server integration
- [ ] Offline fallback capability

### Architecture
```
Teddy Hardware
    ↓
Home Wi-Fi
    ↓
Home AI Server
    ↓
LLM + Memory + Personality
```

### Hardware Considerations
- Low-power Raspberry Pi or STM32-based controller
- Quality microphone (directional)
- Clear speaker
- Visual indicators (eyes/LEDs)
- Durable plush design

---

## Infrastructure Tasks

### Task 1: Git Repository (In Progress)
- [x] Set up project structure
- [ ] Initialize .gitignore
- [ ] Create branch strategy
- [ ] Document contribution guidelines

### Task 2: Raspberry Pi Setup
- [ ] SSH configuration
- [ ] Docker installation
- [ ] Gitea setup
- [ ] Tailscale VPN
- [ ] Database setup
- [ ] Backup system

### Task 3: Windows 11 LLM Setup
- [ ] Ollama installation
- [ ] Model download (Qwen, Llama, Gemma)
- [ ] Performance testing
- [ ] API endpoint configuration
- [ ] Development environment setup

### Task 4: Development Workflow
- [ ] Local development environment
- [ ] Testing framework
- [ ] CI/CD pipeline
- [ ] Documentation generation
- [ ] Release process

---

## Timeline Estimate

| Phase | Duration | Quarter |
|-------|----------|---------|
| Phase 1 (MVP) | 4-6 weeks | Q4 2026 |
| Phase 2 (Memory) | 3-4 weeks | Q1 2027 |
| Phase 3 (Router) | 3-4 weeks | Q1 2027 |
| Phase 4 (Mobile) | 6-8 weeks | Q2 2027 |
| Phase 5 (Physical) | 8-12 weeks | Q3 2027 |

---

## Success Metrics

### Functionality
- Voice pipeline works end-to-end
- Response latency < 2 seconds
- Memory recall accuracy > 95%
- Personality consistency score > 8/10

### Reliability
- Uptime > 99% on home server
- Speech recognition accuracy > 95%
- Error recovery automatic

### Experience
- Child naturally engages with Teddy
- Responses feel personal and appropriate
- No generic chatbot feel
- Long-term memory demonstrated across sessions

---

## Known Risks & Mitigations

### Risk: Local 8B models insufficient quality
**Mitigation:** 
- Build multi-model support early
- Benchmark frequently
- Optional cloud fallback
- Prompt engineering optimization

### Risk: Speech processing latency
**Mitigation:**
- Test with fast models
- Optimize inference
- Consider streaming
- Fallback to text input

### Risk: Privacy concerns with cloud integration
**Mitigation:**
- Local-first by default
- Explicit opt-in for cloud
- Data retention policies
- Regular audits

### Risk: Hardware costs prohibitive
**Mitigation:**
- Use Raspberry Pi as stopgap
- Defer physical Teddy to later phase
- Community hardware sourcing
- 3D printing custom enclosures

---

## Next Steps (Immediate)
1. ✓ Create project structure and documentation
2. Begin Task 2: Raspberry Pi infrastructure setup
3. Begin Task 3: Local LLM setup on Windows 11
4. Create simple Python LLM client
5. Integrate with Ollama API
