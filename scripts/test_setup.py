#!/usr/bin/env python3
"""
Quick test script for Teddy AI setup
Run this after configuring Ollama on Windows
"""

import os
import sys
import requests
import json
from pathlib import Path

import pytest


def check_ollama_connection():
    """Test if we can connect to Ollama."""
    print("\n" + "="*60)
    print("🧸 TEDDY AI - OLLAMA CONNECTION TEST")
    print("="*60 + "\n")

    # Get the configured URL
    ollama_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
    print(f"Attempting to connect to: {ollama_url}")
    print()

    try:
        print("1️⃣  Checking Ollama availability...")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)

        if response.status_code == 200:
            print("   ✅ Ollama is running!")
            data = response.json()
            models = data.get('models', [])

            print(f"\n2️⃣  Available models: {len(models)}")
            for model in models:
                name = model['name']
                size = model.get('size', 0) / (1024**3)  # Convert to GB
                print(f"   ✓ {name} ({size:.1f} GB)")

            if not models:
                print("   ⚠️  No models found. Pull one with: ollama pull qwen:7b")
                return False

            # Test LLM response
            print(f"\n3️⃣  Testing LLM response...")
            model_name = models[0]['name'] if models else "qwen:7b"

            payload = {
                "model": model_name,
                "prompt": "Hello, Teddy!",
                "stream": False,
            }

            response = requests.post(
                f"{ollama_url}/api/generate",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                print(f"   ✅ Model responded!")
                print(f"   Response: {text[:100]}...")
                print(f"   Model: {model_name}")
                print(f"   Tokens: {result.get('total_tokens', 'unknown')}")

                print("\n" + "="*60)
                print("✅ OLLAMA IS READY TO USE!")
                print("="*60)
                print("\nNext steps:")
                print("  1. Run: python scripts/cli.py demo --mode text")
                print("  2. Or: python scripts/cli.py status")
                print()
                return True
            else:
                print(f"   ✗ Model error: {response.status_code}")
                return False

        else:
            print(f"   ✗ HTTP Error: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"   ✗ Connection Failed")
        print(f"\n   Error: {str(e)}")
        print("\n   Troubleshooting:")
        print("   1. Make sure Ollama is running: ollama serve")
        print("   2. Windows IP configured: [Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'User')")
        print("   3. Find Windows IP: ipconfig | Select-String 'IPv4'")
        print("   4. Update URL: export OLLAMA_API_URL=\"http://YOUR_IP:11434\"")
        print("   5. Check Windows Firewall: Allow port 11434")
        return False

    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False


def test_ollama_connection():
    """Test if we can connect to Ollama."""
    if not check_ollama_connection():
        pytest.skip("Ollama is not running or not configured in this environment")


def check_project_structure():
    """Verify project structure is complete."""
    print("\n4️⃣  Checking project structure...")

    required_dirs = [
        'ai', 'backend', 'config', 'docs', 'memory',
        'personality', 'scripts', 'voice'
    ]

    required_files = [
        'README.md', 'requirements.txt', 'config/teddy.yaml',
        'scripts/cli.py', 'backend/services/teddy_service.py'
    ]

    missing = []
    for d in required_dirs:
        if not Path(d).exists():
            missing.append(f"Directory: {d}")

    for f in required_files:
        if not Path(f).exists():
            missing.append(f"File: {f}")

    if missing:
        print(f"   ✗ Missing: {len(missing)} items")
        for item in missing:
            print(f"      - {item}")
        return False
    else:
        print(f"   ✅ All {len(required_dirs)} directories found")
        print(f"   ✅ All {len(required_files)} core files found")
        return True


def test_project_structure():
    """Verify project structure is complete."""
    assert check_project_structure()


def main():
    """Run all tests."""
    print("\n")

    # Test project structure
    structure_ok = check_project_structure()

    # Test Ollama connection
    ollama_ok = check_ollama_connection()

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Project Structure: {'✅ OK' if structure_ok else '❌ Issues'}")
    print(f"Ollama Connection: {'✅ OK' if ollama_ok else '⚠️  Needs Setup'}")

    if structure_ok and ollama_ok:
        print("\n🎉 Everything is ready! Run:")
        print("   python scripts/cli.py demo --mode text")

    print()
    return 0 if (structure_ok and ollama_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
