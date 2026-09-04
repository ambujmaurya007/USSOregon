# 🧸 Complete Setup: Windows Ollama + Container Development

## Current Status
✅ Python environment set up in container  
✅ qwen:7b model downloaded on Windows  
❌ Ollama needs network configuration  

## What You Need to Do (5 minutes)

### Step 1: Configure Ollama to Listen on Network (Windows)

**Option A: Permanent Configuration (Recommended)**

In **PowerShell as Administrator**:

```powershell
# Set environment variable to listen on all interfaces
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0:11434", "User")

# Verify it was set
[Environment]::GetEnvironmentVariable("OLLAMA_HOST", "User")
# Should output: 0.0.0.0:11434

# Stop current Ollama
Stop-Process -Name ollama -Force -ErrorAction SilentlyContinue

# Restart Ollama (it will now listen on all interfaces)
ollama serve
```

You should see output like:
```
binding 0.0.0.0:11434
```

**Option B: One-Time Configuration (Temporary)**

In **Command Prompt**:
```cmd
set OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

### Step 2: Find Your Windows IP Address

In PowerShell:
```powershell
ipconfig /all
```

Look for **IPv4 Address** - typically looks like: `192.168.x.x` or `10.x.x.x`

Example:
```
Ethernet adapter Ethernet:
   IPv4 Address. . . . . . . . . . . . : 192.168.1.105
   Subnet Mask . . . . . . . . . . . . : 255.255.255.0
```

### Step 3: Test Connection from Windows

In PowerShell:
```powershell
# Test if Ollama is accessible
curl http://localhost:11434/api/tags -UseBasicParsing

# Test from another IP
curl http://YOUR_IP:11434/api/tags -UseBasicParsing
# Example: curl http://192.168.1.105:11434/api/tags -UseBasicParsing
```

Should see response with model info.

### Step 4: Update Container Configuration

In the **VS Code terminal** (container):

```bash
cd /workspaces/USSOregon
source venv/bin/activate

# Set your Windows IP
export OLLAMA_API_URL="http://192.168.1.105:11434"  # Use YOUR IP from Step 2

# Test the connection
python scripts/cli.py test llm
```

Or update the config file permanently:

Edit `config/teddy.yaml`:
```yaml
llm:
  providers:
    ollama:
      api_url: "http://192.168.1.105:11434"  # Your Windows IP
      model: "qwen:7b"
```

### Step 5: Verify Everything Works

```bash
source venv/bin/activate

# Check status
python scripts/cli.py status

# Test LLM connection
python scripts/cli.py test llm

# Run interactive demo
python scripts/cli.py demo --mode text
```

## Complete Quick Reference

```powershell
# ===== ON WINDOWS (PowerShell as Admin) =====

# 1. Stop and configure Ollama
Stop-Process -Name ollama -Force -ErrorAction SilentlyContinue
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0:11434", "User")
ollama serve

# 2. In another PowerShell:
ipconfig  # Find IPv4 Address

# 3. Test it works
curl http://localhost:11434/api/tags -UseBasicParsing
```

```bash
# ===== IN CONTAINER (VS Code Terminal) =====

# 1. Navigate and activate
cd /workspaces/USSOregon
source venv/bin/activate

# 2. Set Windows IP (use your actual IP)
export OLLAMA_API_URL="http://192.168.1.105:11434"

# 3. Test
python scripts/cli.py test llm

# 4. Try demo
python scripts/cli.py demo --mode text
```

## Troubleshooting

### "Connection refused"
- Make sure `ollama serve` is running on Windows
- Check firewall isn't blocking port 11434
- Verify Windows IP is correct with `ipconfig`

### "Address already in use"
- Port 11434 is taken
- Kill process: `Stop-Process -Name ollama -Force`
- Try different port in OLLAMA_HOST

### Can't find Windows IP
```powershell
# List all network info
ipconfig /all

# Just show IPv4
ipconfig | Select-String "IPv4"
```

### Still can't connect from container
- Make sure you're using the correct Windows IP (not 127.0.0.1)
- Windows Firewall might be blocking - add exception for port 11434
- Try with your computer name instead: `http://COMPUTER-NAME:11434`

## Once Connected, You Have:

✅ Full voice pipeline ready  
✅ Memory system working  
✅ Personality engine active  
✅ Local LLM responding  

Next: [Run the interactive demo!](#step-5-verify-everything-works)

---

**Having issues?** See [OLLAMA_CONNECTION.md](OLLAMA_CONNECTION.md) for more details.
