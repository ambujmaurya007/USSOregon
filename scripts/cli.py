"""
Simple CLI for testing Teddy AI components
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Teddy AI - Local-first AI companion for children"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check system status")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test components")
    test_parser.add_argument(
        "component",
        choices=["llm", "stt", "tts", "memory", "all"],
        help="Component to test"
    )
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run interactive demo")
    demo_parser.add_argument(
        "--mode",
        choices=["voice", "text"],
        default="text",
        help="Demo mode"
    )
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup and configure")
    setup_parser.add_argument(
        "--child-name",
        help="Child's name"
    )
    setup_parser.add_argument(
        "--age",
        type=int,
        help="Child's age"
    )
    
    args = parser.parse_args()
    
    if args.command == "status":
        print_status()
    elif args.command == "test":
        run_tests(args.component)
    elif args.command == "demo":
        run_demo(args.mode)
    elif args.command == "setup":
        run_setup(args)
    else:
        parser.print_help()


def print_status():
    """Print system status."""
    print("🧸 Teddy AI Status\n")
    print("Component Status:")
    print("  ✓ Project Structure")
    print("  ✓ Configuration")
    print("  ⏳ LLM Provider (requires Ollama)")
    print("  ⏳ Speech-to-Text (requires Whisper)")
    print("  ⏳ Text-to-Speech (requires Piper)")
    print("  ✓ Memory Backend")
    print("  ✓ Personality Engine")
    print("\n👉 Next: Install dependencies with: pip install -r requirements.txt")


def run_tests(component):
    """Run component tests."""
    print(f"🧪 Testing {component} component...\n")
    
    if component in ["memory", "all"]:
        test_memory()
    
    if component in ["llm", "all"]:
        test_llm()
    
    if component in ["stt", "all"]:
        test_stt()
    
    if component in ["tts", "all"]:
        test_tts()


def test_memory():
    """Test memory backend."""
    print("  Memory Backend: ", end="", flush=True)
    try:
        from memory.long_term.memory_backend import SQLiteMemoryBackend
        backend = SQLiteMemoryBackend("./data/teddy_test.db")
        
        # Test store
        memory_id = backend.store("test", "Test memory")
        
        # Test retrieve
        memories = backend.retrieve("test")
        
        if memories and memories[0].content == "Test memory":
            print("✓\n")
        else:
            print("✗ (retrieval failed)\n")
    except Exception as e:
        print(f"✗ ({str(e)})\n")


def test_llm():
    """Test LLM provider."""
    print("  LLM Provider (Ollama): ", end="", flush=True)
    try:
        from ai.providers.ollama_provider import OllamaProvider
        provider = OllamaProvider({
            "api_url": "http://localhost:11434",
            "model": "qwen:7b"
        })
        
        if provider.is_available():
            print("✓\n")
        else:
            print("✗ (not available - is Ollama running?)\n")
    except Exception as e:
        print(f"✗ ({str(e)})\n")


def test_stt():
    """Test speech-to-text."""
    print("  Speech-to-Text (Whisper): ", end="", flush=True)
    try:
        from voice.stt.stt_engine import WhisperSTTEngine
        engine = WhisperSTTEngine({"model": "tiny"})
        
        if engine.is_available():
            print("✓\n")
        else:
            print("✗ (not initialized)\n")
    except ImportError:
        print("✗ (Whisper not installed)\n")
    except Exception as e:
        print(f"✗ ({str(e)})\n")


def test_tts():
    """Test text-to-speech."""
    print("  Text-to-Speech (Piper): ", end="", flush=True)
    try:
        import yaml
        from voice.tts.tts_engine import PiperTTSEngine
        project_root = Path(__file__).parent.parent
        with open(project_root / "config" / "teddy.yaml") as config_file:
            config = yaml.safe_load(config_file) or {}
        tts_config = config.get("voice", {}).get("tts", {})
        engine = PiperTTSEngine(tts_config.get("config", {}))
        
        if engine.is_available():
            print("✓\n")
        else:
            print("✗ (not initialized)\n")
    except ImportError:
        print("✗ (Piper not installed)\n")
    except Exception as e:
        print(f"✗ ({str(e)})\n")


def run_demo(mode):
    """Run interactive demo."""
    print(f"🎭 Teddy AI Demo ({mode} mode)\n")
    
    if mode == "text":
        import yaml
        from backend.services.teddy_service import TeddyAIService

        project_root = Path(__file__).parent.parent
        with open(project_root / "config" / "teddy.yaml") as config_file:
            config = yaml.safe_load(config_file) or {}

        teddy = TeddyAIService(config)
        if not teddy.llm_provider or not teddy.llm_provider.is_available():
            print("Ollama is not available. Start it with: ollama serve")
            return

        tts_engine = None
        try:
            from voice.tts.tts_engine import PiperTTSEngine

            tts_config = config.get("voice", {}).get("tts", {})
            if tts_config.get("engine") == "piper":
                tts_engine = PiperTTSEngine(tts_config.get("config", {}))
        except RuntimeError as error:
            print(f"Audio output unavailable: {error}")

        print("Type messages to Teddy (press Ctrl+C to quit):\n")
        try:
            while True:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                
                response_text = teddy.ask(user_input)
                companion_name = teddy.personality_engine.personality.name
                print(f"{companion_name}: {response_text}")
                if tts_engine:
                    audio_path = project_root / "data" / "response.wav"
                    tts_result = tts_engine.synthesize(response_text, str(audio_path))
                    print(f"Audio: {tts_result.audio_path}")
                print()
        except RuntimeError as error:
            print(f"\nUnable to generate a response: {error}")
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
    else:
        print("Voice demo requires Whisper and Piper installation.")
        print("Install with: pip install -r requirements.txt")


def run_setup(args):
    """Run setup configuration."""
    print("⚙️  Teddy AI Setup\n")
    
    # Load or create config
    import yaml
    config_path = Path("config/teddy.yaml")
    
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
    else:
        config = {"child": {}}
    
    # Update from args
    if args.child_name:
        config["child"]["name"] = args.child_name
    if args.age:
        config["child"]["age"] = args.age
    
    # Prompt for missing info
    if not config["child"].get("name"):
        config["child"]["name"] = input("Child's name: ").strip()
    
    if not config["child"].get("age"):
        age = input("Child's age: ").strip()
        config["child"]["age"] = int(age) if age.isdigit() else 0
    
    # Save
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("\n✅ Configuration saved!")
    print(f"  Child name: {config['child']['name']}")
    print(f"  Child age: {config['child']['age']}")


if __name__ == "__main__":
    main()
