"""
Simple CLI for testing Teddy AI components
"""

import sys
import argparse
import re
import random
from difflib import SequenceMatcher
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from voice.conversation_state import (
    ConversationState,
    ACTIVITIES,
    activity_label,
    activity_prompt,
    alternative_question,
    begin_activity,
    detect_activity_intent,
    detect_language,
    resolve_selection,
)
from voice.interactive_counting import InteractiveCounting


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
    demo_parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="Seconds to record in voice mode"
    )
    demo_parser.add_argument(
        "--device",
        help="Microphone device index or name in voice mode"
    )
    demo_parser.add_argument(
        "--wake-word",
        help="Word that activates voice mode (default: Emma)"
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
        run_demo(args.mode, args.duration, args.device, args.wake_word)
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


def run_demo(mode, duration=5.0, device=None, wake_word=None):
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
        import yaml
        from backend.services.teddy_service import TeddyAIService
        from voice.audio.microphone import MicrophoneRecorder

        project_root = Path(__file__).parent.parent
        with open(project_root / "config" / "teddy.yaml") as config_file:
            config = yaml.safe_load(config_file) or {}

        audio_config = config.get("voice", {}).get("audio", {}).copy()
        if device is not None:
            audio_config["device"] = int(device) if device.isdigit() else device

        recorder = MicrophoneRecorder(audio_config)
        if not recorder.is_available():
            print("No microphone input device is available.")
            return

        teddy = TeddyAIService(config)
        configured_wake_word = audio_config.get("wake_word", "Emma")
        active_wake_word = (wake_word or configured_wake_word).strip()
        chunk_duration = float(audio_config.get("listen_chunk_seconds", 2.0))
        print(
            f"Always listening for '{active_wake_word}'. "
            "Say the wake word, then your request; press Ctrl+C to quit."
        )
        try:
            _run_wake_word_loop(
                teddy,
                recorder,
                project_root,
                active_wake_word,
                chunk_duration,
                duration,
            )
        except KeyboardInterrupt:
            print("\nGoodbye!")


def _run_wake_word_loop(
    teddy,
    recorder,
    project_root,
    wake_word,
    chunk_duration,
    command_duration,
):
    """Listen continuously and process speech after the configured wake word."""
    import winsound

    wake_pattern = re.compile(rf"\b{re.escape(wake_word)}\b", re.IGNORECASE)
    input_audio_path = project_root / "data" / "microphone.wav"
    show_heard_text = teddy.config.get("voice", {}).get("audio", {}).get(
        "show_heard_text", False
    )
    intent_words = teddy.config.get("voice", {}).get("audio", {}).get(
        "intent_words", {}
    )
    conversation_state = ConversationState()

    while True:
        recorder.record(chunk_duration, input_audio_path)
        detected_text = teddy.stt_engine.transcribe(
            str(input_audio_path),
            initial_prompt=(
                f"{wake_word}. Child requests may include poem, poems, story, "
                "tale, song, animal, numbers, colors, bedtime, sunao, kahani, "
                "chanda, chand, haathi, sher, machli, and mujhe."
            ),
        ).text.strip()
        if not detected_text:
            continue

        if show_heard_text:
            print(f"Heard: {detected_text}")
        match = wake_pattern.search(detected_text)
        if not match:
            continue

        request_text = detected_text[match.end():].strip(" ,.!?")
        print(f"\n[{wake_word} heard]")
        _announce_listening(teddy, project_root, winsound)
        if not request_text:
            print(f"Listening for your request ({command_duration:g} seconds)...")
            recorder.record(command_duration, input_audio_path)
            request_text = teddy.stt_engine.transcribe(
                str(input_audio_path),
                initial_prompt=(
                    "Child request vocabulary: poem, poems, story, tale, "
                    "song, animal, numbers, colors, bedtime, sunao, kahani, "
                    "chanda, chand, haathi, sher, machli, and mujhe."
                ),
                language="auto",
            ).text.strip()
            if not request_text:
                print("I did not quite hear that. Please try again.")
                continue

        print(f"You: {request_text}")
        conversation_state.conversation_language = detect_language(
            request_text, conversation_state.conversation_language
        )
        print(f"Language: {conversation_state.conversation_language}")
        intent = _detect_intent(request_text, intent_words)
        if intent:
            print(f"Intent: {intent.title()}")
        requested_activity = detect_activity_intent(request_text)
        if _is_counting_request(request_text):
            _run_counting_activity(
                teddy,
                recorder,
                project_root,
                input_audio_path,
                command_duration,
                winsound,
            )
            continue
        activity_question = begin_activity(request_text, conversation_state)
        selected_activity = (
            conversation_state.selected_item if requested_activity else None
        )
        stop_requested = False
        if activity_question:
            try:
                knowledge_choices = _knowledge_choices(teddy, conversation_state.last_intent)
                if knowledge_choices:
                    activity_question = _knowledge_choice_question(
                        conversation_state.last_intent, knowledge_choices
                    )
                _speak_text(teddy, project_root, winsound, activity_question, "choice.wav")
                print(activity_question)
                while conversation_state.awaiting_selection:
                    print(f"Listening for your choice ({command_duration:g} seconds)...")
                    follow_up = _capture_follow_up(
                        teddy, recorder, input_audio_path, command_duration
                    )
                    if not follow_up:
                        selected_activity = _random_knowledge_activity(
                            teddy, conversation_state.last_intent, knowledge_choices
                        )
                        if selected_activity:
                            conversation_state.awaiting_selection = False
                            conversation_state.selected_item = selected_activity
                            conversation_state.last_activity = selected_activity
                            print(f"I did not hear a choice, so I picked {selected_activity}.")
                            break
                        print("I did not quite hear that. Please choose one.")
                        continue
                    print(f"Heard: {follow_up}")
                    conversation_state.conversation_language = detect_language(
                        follow_up, conversation_state.conversation_language
                    )
                    selection = resolve_selection(follow_up, conversation_state)
                    if selection == "ask_alternative":
                        activity_question = alternative_question(conversation_state)
                        _speak_text(teddy, project_root, winsound, activity_question, "choice.wav")
                        print(activity_question)
                    elif selection == "stop":
                        print("Okay, we can stop.")
                        stop_requested = True
                        break
                    elif selection == "again":
                        selected_activity = conversation_state.last_activity
                    elif selection:
                        selected_activity = selection
                    else:
                        print("You can say a choice, yes, or no.")
                if selected_activity is None and conversation_state.awaiting_selection:
                    continue
            except Exception as error:
                print(f"Activity choice failed: {error}")
                continue
        if stop_requested:
            continue
        if selected_activity:
            print(f"Selected activity: {selected_activity}")
        if selected_activity:
            request_for_emma = (
                activity_prompt(selected_activity)
                if selected_activity in ACTIVITIES
                else f"Perform the exact local activity named {selected_activity}."
            )
        elif resolve_selection(request_text, conversation_state) == "again":
            selected_activity = conversation_state.last_activity
            request_for_emma = activity_prompt(selected_activity)
            print("Emma: Of course! Here it comes again.")
        elif re.search(r"\b(stop|enough|finished|done)\b", request_text, re.IGNORECASE):
            print("Okay, we can stop.")
            continue
        elif _needs_activity_confirmation(request_text):
            try:
                confirmation = _confirm_activity(
                    teddy,
                    recorder,
                    project_root,
                    input_audio_path,
                    command_duration,
                    winsound,
                    request_text,
                )
            except Exception as error:
                print(f"Confirmation failed: {error}")
                continue
            if confirmation is False:
                print("Okay, we can try something else.")
                continue
            if confirmation is None:
                print("I didn't hear a clear yes. Say Emma when you're ready to try again.")
                continue
            print("Okay, I'll do that.")
            request_for_emma = request_text
        else:
            request_for_emma = request_text

        try:
            print("Thinking...")
            exact_content = (
                teddy.get_exact_knowledge(
                    activity_label(selected_activity)
                    if selected_activity in ACTIVITIES
                    else selected_activity
                )
                if selected_activity
                else None
            )
            if exact_content:
                response_text = exact_content
                print("Using exact text from Emma's knowledge library.")
            else:
                response_text = teddy.ask(
                    request_for_emma,
                    language=conversation_state.conversation_language,
                )
            response_audio_path = _synthesize_response(teddy, response_text, project_root)
        except Exception as error:
            print(f"Voice response failed: {error}")
            continue

        companion_name = teddy.personality_engine.personality.name
        print(f"{companion_name}: {response_text}")
        print(f"Audio saved to: {response_audio_path}")
        winsound.PlaySound(response_audio_path, winsound.SND_FILENAME)


def _needs_activity_confirmation(request_text):
    """Keep confirmation enabled for every request captured by voice mode."""
    return bool(request_text.strip())


def _is_counting_request(request_text):
    """Identify the dedicated interactive counting activity."""
    return bool(re.search(
        r"\b(number|numbers|count|counting|math|ginti)\b|"
        r"\b(counting|ginti)\s+(karna|karein|seekhna)\b",
        request_text.casefold(),
    ))


def _run_counting_activity(
    teddy,
    recorder,
    project_root,
    input_audio_path,
    command_duration,
    winsound,
):
    """Run counting with deterministic prompts and child-response retries."""
    activity = InteractiveCounting()
    _speak_text(teddy, project_root, winsound, activity.opening(), "counting.wav")
    print(f"Emma: {activity.opening()}")

    while activity.awaiting_response:
        prompt = activity.prompt()
        _speak_text(teddy, project_root, winsound, prompt, "counting_prompt.wav")
        print(f"Emma: {prompt}")
        response = _capture_follow_up(
            teddy, recorder, input_audio_path, command_duration
        )
        if not response:
            response = ""
        print(f"Heard: {response or '[no response]'}")
        step = activity.handle(response)
        _speak_text(teddy, project_root, winsound, step.message, "counting_reply.wav")
        print(f"Emma: {step.message}")
        if step.finished or step.stopped:
            break


def _capture_follow_up(teddy, recorder, input_audio_path, command_duration):
    """Capture the child's next answer without requiring the wake word again."""
    recorder.record(command_duration, input_audio_path)
    return teddy.stt_engine.transcribe(
        str(input_audio_path),
        initial_prompt=(
            "Child activity choices: yes, no, Twinkle Twinkle, animal poem, "
            "funny poem, bedtime poem, Baby Shark, lullaby, lion, animal, space."
        ),
        language="auto",
    ).text.strip()


def _knowledge_choices(teddy, intent):
    """Return exact local sources matching the current activity family."""
    if not teddy.knowledge_base:
        return []
    category = {
        "poem_request": "poem",
        "song_request": "song",
    }.get(intent)
    if not category:
        return []
    return teddy.knowledge_base.list_exact(category)


def _knowledge_choice_question(intent, choices):
    """Ask a choice question using only content actually available locally."""
    labels = [
        (choice.metadata.get("aliases") or [choice.metadata.get("title", choice.source)])[0]
        for choice in choices[:4]
    ]
    if intent == "poem_request":
        kind = "poem"
    else:
        kind = "song"
    if len(labels) == 1:
        return f"I know one {kind}: {labels[0]}. Would you like that one?"
    return f"Which {kind} would you like: " + ", ".join(labels[:-1]) + f", or {labels[-1]}?"


def _random_knowledge_activity(teddy, intent, choices):
    """Choose a real local exact source when the child gives no answer."""
    if not choices:
        return None
    selected = random.choice(choices)
    aliases = selected.metadata.get("aliases", [])
    return aliases[0] if aliases else selected.metadata.get("title", selected.source)


def _speak_text(teddy, project_root, winsound, text, filename):
    """Speak a short interaction prompt through Emma's configured TTS."""
    if not teddy.tts_engine:
        raise RuntimeError("Text-to-speech is not available")
    audio_path = project_root / "data" / filename
    result = teddy.tts_engine.synthesize(text, str(audio_path))
    winsound.PlaySound(result.audio_path, winsound.SND_FILENAME)


def _contains_word_or_variant(request_text, words):
    """Match an activity word even when Whisper adds punctuation or a suffix."""
    tokens = re.findall(r"[a-z]+", request_text.lower())
    for token in tokens:
        if token in words:
            return True
        if any(SequenceMatcher(None, token, word).ratio() >= 0.8 for word in words):
            return True
    return False


def _detect_intent(request_text, intent_words):
    """Return the first configured child-friendly intent found in a request."""
    for intent, words in intent_words.items():
        if _contains_word_or_variant(request_text, set(words)):
            return intent
    return None


def _confirm_activity(
    teddy,
    recorder,
    project_root,
    input_audio_path,
    command_duration,
    winsound,
    request_text,
):
    """Ask whether the child wants the requested story or poem before starting."""
    if _contains_word_or_variant(request_text, {"poem", "poems", "poetry", "rhyme", "rhymes", "rhyming"}):
        question = "Would you like me to recite a poem?"
    elif _contains_word_or_variant(request_text, {"story", "katha", "tale", "bedtime"}):
        question = "Would you like me to tell a story?"
    elif _contains_word_or_variant(request_text, {"song", "sing", "music", "lullaby"}):
        question = "Would you like me to sing a song?"
    else:
        question = "Would you like me to help with that?"
    print(f"Emma: {question}")
    question_path = project_root / "data" / "confirmation.wav"
    question_result = teddy.tts_engine.synthesize(question, str(question_path))
    winsound.PlaySound(question_result.audio_path, winsound.SND_FILENAME)
    print(f"Listening for your answer ({command_duration:g} seconds)...")
    recorder.record(command_duration, input_audio_path)
    answer = teddy.stt_engine.transcribe(str(input_audio_path)).text.strip().lower()
    print(f"Heard: {answer}")
    if re.search(r"\b(no|stop|not now|cancel)\b", answer):
        return False
    if re.search(r"\b(yes|yeah|yep|sure|please|okay|ok)\b", answer):
        return True
    return None


def _announce_listening(teddy, project_root, winsound):
    """Give immediate visual and audible confirmation after wake-word detection."""
    print("Listening...")
    try:
        winsound.Beep(880, 120)
    except RuntimeError:
        pass

    if not teddy.tts_engine:
        return

    try:
        audio_path = project_root / "data" / "listening.wav"
        result = teddy.tts_engine.synthesize("Listening.", str(audio_path))
        winsound.PlaySound(result.audio_path, winsound.SND_FILENAME)
    except RuntimeError as error:
        print(f"Audio acknowledgement unavailable: {error}")


def _synthesize_response(teddy, response_text, project_root):
    """Create the spoken response for a request already transcribed by Whisper."""
    if not teddy.tts_engine:
        raise RuntimeError("Text-to-speech is not available; install and configure Piper")
    audio_path = project_root / "data" / "response.wav"
    result = teddy.tts_engine.synthesize(response_text, str(audio_path))
    return result.audio_path


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
