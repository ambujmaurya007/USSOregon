# Architecture Decision Records (ADRs)

## ADR-001: Local-First Architecture

### Decision
All processing happens locally by default. Cloud services are optional and must be explicitly configured.

### Rationale
- **Privacy:** Personal interactions and memories stay on home network
- **Latency:** Lower latency for voice interaction
- **Reliability:** Offline operation possible
- **Cost:** No recurring cloud costs

### Implementation
- Local SQLite for memory
- Local LLM (Ollama/vLLM) for inference
- Local STT/TTS where possible
- Cloud APIs loaded conditionally

### Consequences
- Higher initial setup complexity
- More resources required on-device
- Must support multiple model families for quality
- Requires hardware investment

---

## ADR-002: Model Abstraction Layer

### Decision
Implement a provider interface that abstracts specific LLM implementations. Support multiple model families (Qwen, Llama, Gemma) with pluggable providers.

### Rationale
- **Future-proof:** Easy to adopt better models as they emerge
- **Flexibility:** Switch models without rewriting application
- **Testing:** Benchmark different models objectively
- **Fallback:** Cloud LLM as fallback without major refactoring

### Implementation
```python
class LLMProvider(ABC):
    def generate(self, prompt: str, context: dict) -> str:
        pass

class QwenProvider(LLMProvider):
    ...

class LlamaProvider(LLMProvider):
    ...

class CloudProvider(LLMProvider):  # Optional
    ...
```

### Consequences
- Additional abstraction layer to maintain
- Training/documentation needed
- Slight performance overhead (negligible)

---

## ADR-003: Separate Personality from LLM

### Decision
Personality (rules, tone, constraints) is constructed separately from LLM selection. Prompts dynamically combine:
1. Teddy personality template
2. Child profile
3. Relevant memories
4. Current request

### Rationale
- **Consistency:** Personality persists across model changes
- **Adaptability:** Personality can be tuned without retraining models
- **Multi-language:** Personality templates can be multilingual
- **Auditability:** Understand what prompt is sent to LLM

### Implementation
```
Personality Template (YAML/JSON)
    +
Child Profile (loaded from memory)
    +
Relevant Memories (retrieved from DB)
    +
Current Request
    = Final Prompt to LLM
```

### Consequences
- More complex prompt management
- Requires careful template design
- Testing must cover personality + model combinations

---

## ADR-004: Hybrid Memory System

### Decision
Implement two-tier memory:
- **Short-term:** Current conversation context (LLM context window)
- **Long-term:** Persistent facts and preferences (SQLite)

### Rationale
- **Scalability:** Long-term memory doesn't fill LLM context window
- **Efficiency:** Only relevant memories retrieved per query
- **Persistence:** Survives across sessions
- **Flexibility:** Memory can be queried and modified independently

### Implementation
```
Request Processing:
1. Current conversation → Short-term context
2. Query long-term memory for relevant facts
3. Combine → Full context for LLM
4. After response → Update long-term memory if needed
```

### Consequences
- Memory retrieval must be fast
- Need semantic search or tagging system
- Risk of missing relevant context if retrieval fails

---

## ADR-005: Raspberry Pi as Infrastructure Hub

### Decision
Raspberry Pi acts as always-on development infrastructure server, NOT primary LLM inference machine.

### Rationale
- **Reliability:** Always-on availability
- **Network Hub:** Central point for git, documentation, config
- **Lightweight:** Suitable for non-compute tasks
- **Future-proof:** Separates infrastructure from compute

### Services on Raspberry Pi
- Git server (Gitea)
- Documentation
- Configuration management
- SQLite database (initially)
- Remote access (Tailscale)
- Backup coordination

### LLM Execution
- Windows 11 primary
- Future: dedicated mini PC with GPU
- Scales independently from infrastructure

### Consequences
- Multiple machines to manage
- Network communication required
- Database synchronization needed (if scaling to multiple nodes)

---

## ADR-006: Voice-First UX

### Decision
Voice is the primary interaction mode. Text is secondary/fallback.

### Rationale
- **Child-friendly:** Natural for young users
- **Immersive:** More engaging than text
- **Accessibility:** Works regardless of reading ability
- **Teddy metaphor:** Makes Teddy feel more real

### Implementation
```
Preferred: Voice → STT → LLM → TTS → Voice
Fallback: Text → LLM → TTS (or text output)
```

### Consequences
- Requires robust STT/TTS
- Speech processing adds latency
- Acoustic environment matters
- Accessibility requires good speaker/microphone

---

## ADR-007: Model-Agnostic AI Router

### Decision
AI Router classifies request type and selects model, but doesn't implement model logic. Routing is rule-based, not ML-based (initially).

### Rationale
- **Simplicity:** Easy to understand and debug
- **Deterministic:** Predictable behavior
- **Low-overhead:** No additional model inference
- **Flexibility:** Can upgrade to ML-based later

### Routing Rules (Example)
```
Story Request → Qwen 32B (best storytelling)
Conversation → Llama 13B (efficient, friendly)
Math Question → Gemma 27B (reasoning)
Simple Chat → Qwen 7B (fast, low latency)
Complex Query → Cloud Claude (if configured & fallback enabled)
```

### Consequences
- Manual rule maintenance
- Risk of wrong routing if rules aren't updated
- Could add ML-based routing later

---

## ADR-008: Modular Component Design

### Decision
Every major component has a pluggable interface:
- LLM Providers
- STT Engines
- TTS Engines
- Memory Backends
- Personality Engines

### Rationale
- **Testability:** Easy to mock/swap components
- **Flexibility:** Upgrade without rewrite
- **Parallelization:** Teams can work independently
- **Experimentation:** Test alternatives

### Implementation
```
Base Classes/ABCs:
  - Provider (abstract LLM)
  - STTEngine (abstract speech-to-text)
  - TTSEngine (abstract text-to-speech)
  - MemoryBackend (abstract storage)
  - PersonalityEngine (abstract prompt construction)

Implementations:
  - Ollama/vLLM (LLM)
  - Whisper (STT)
  - Piper (TTS)
  - SQLite (Memory)
  - YAML-based (Personality)
```

### Consequences
- More interfaces to maintain
- Onboarding complexity
- Testing effort increases
- Worth the investment for long-term flexibility

---

## ADR-009: Configuration Over Code

### Decision
Major system configuration (models, APIs, features) is in config files, not hardcoded.

### Rationale
- **User Control:** Parents can configure their setup
- **Deployment:** Different configs for dev/test/prod
- **Security:** Secrets managed separately
- **No Rebuild:** Change behavior without redeployment

### Implementation
```yaml
# config/teddy.yaml
models:
  default: qwen-7b
  fallback: llama-13b
  cloud:
    enabled: false
    provider: openai

voice:
  stt:
    engine: whisper
    language: en
  tts:
    engine: piper
    voice: jenny

memory:
  backend: sqlite
  path: ./data/teddy.db
```

### Consequences
- Config file complexity
- Validation needed
- Default configs must work

---

## ADR-010: Defer Physical Teddy

### Decision
Initial MVP is software/mobile only. Physical Teddy comes after MVP is stable and proven.

### Rationale
- **Faster iteration:** Software easier to update than hardware
- **Cost:** Hardware development is expensive
- **Learning:** Understand user needs first
- **Reusability:** Software works regardless of hardware iteration

### Timeline
- Phase 1-2: Software MVP
- Phase 3-4: Mobile app
- Phase 5: Physical embodiment

### Consequences
- Delays "teddy" feeling (mitigated by voice)
- Less tangible for parent/child
- Must design software to support hardware later

---

## Future Decision Points

These will be decided after MVP validation:

1. **Mobile Framework:** React Native vs Flutter vs native?
2. **Database Scaling:** SQLite → PostgreSQL or Vector DB?
3. **Cloud Integration:** OpenAI, Anthropic, local alternative?
4. **Physical Teddy Design:** Specific hardware spec?
5. **Multi-child Support:** Single child vs multiple?
6. **Security Model:** Encryption at rest/transit?
7. **Monitoring:** Telemetry and usage insights?

