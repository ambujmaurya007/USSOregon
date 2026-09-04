# Connecting to Windows Ollama from Container

## Current Setup
- **Windows Machine:** Ollama running on port 11434
- **Container:** Dev environment (needs to connect to Windows Ollama)
- **Model:** qwen:7b (already downloaded)

## Step 1: Check Your Windows IP Address

In PowerShell on Windows:
```powershell
ipconfig
```

Look for **IPv4 Address** (typically `192.168.x.x` or `10.x.x.x`)

Example output:
```
Ethernet adapter Ethernet:
   IPv4 Address. . . . . . . . . . . . : 192.168.1.100
```

## Step 2: Configure Ollama to Accept Remote Connections

In PowerShell (on Windows):
```powershell
# Stop any running Ollama instances
Stop-Process -Name ollama -Force

# Set to listen on all interfaces
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0:11434", "User")

# Restart Ollama
ollama serve
```

You should see:
```
binding 0.0.0.0:11434
```

## Step 3: Update Container Configuration

### Option A: Using Your Windows IP (Recommended)
Edit the config file or use environment variable:

```bash
# In the container
export OLLAMA_API_URL="http://192.168.1.100:11434"  # Replace with your Windows IP
python scripts/cli.py status
```

### Option B: Quick Test Script
In the container, create `test_ollama.py`:

```python
import requests
import os

# Try different connection methods
urls = [
    "http://localhost:11434",
    "http://host.docker.internal:11434",  # Docker Desktop
    os.getenv("OLLAMA_API_URL", "http://localhost:11434")
]

for url in urls:
    try:
        response = requests.get(f"{url}/api/tags", timeout=2)
        print(f"✓ Connected to {url}")
        print(f"  Models: {len(response.json().get('models', []))}")
        break
    except Exception as e:
        print(f"✗ Cannot connect to {url}")
```

## Step 4: Setup Development Environment

```bash
cd /workspaces/USSOregon
bash scripts/setup_dev.sh
source venv/bin/activate
python scripts/cli.py status
```

## Troubleshooting

### "Connection refused"
- Make sure Ollama is running on Windows: `ollama serve`
- Verify port isn't blocked by firewall
- Check that you're using the correct Windows IP

### "Only one usage of each socket address"
- Another process is using port 11434
- Kill all Ollama processes and retry

### Still can't connect
- Run from Windows: `curl http://localhost:11434/api/tags` to verify Ollama works locally
- Then use the same IP your container machine uses to reach your Windows machine

## Docker Desktop Tip

If using Docker Desktop, try:
```bash
export OLLAMA_API_URL="http://host.docker.internal:11434"
```

This is the special Docker hostname for the host machine.

## Quick Connection Verification

```bash
# Install curl in container if needed
apt-get update && apt-get install -y curl

# Test connection
curl http://YOUR_WINDOWS_IP:11434/api/tags
```

Should return something like:
```json
{"models":[{"name":"qwen:7b","modified_at":"..."}]}
```

---

Once connected, you can test the full pipeline!
