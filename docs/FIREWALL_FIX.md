# 🔥 Firewall Troubleshooting for Ollama

## Problem
Container can't reach Ollama on Windows because the firewall is blocking port 11434.

## Solution

### Option 1: Allow Ollama Through Windows Firewall (Recommended)

**Step 1:** Open Windows Security
- Press `Win + I` to open Settings
- Go to **Privacy & Security** → **Windows Defender Firewall**

**Step 2:** Allow an app through firewall
- Click **Allow an app through firewall**
- Click **Change settings**
- Click **Allow another app**

**Step 3:** Add Ollama
- Click **Browse**
- Navigate to: `C:\Users\HARSH\AppData\Local\Programs\Ollama\ollama.exe`
- Select it and click **Add**

**Step 4:** Configure for Private Networks
- Make sure **Private** is checked for Ollama
- Click **OK**

---

### Option 2: Quick Fix - Temporarily Disable Firewall (Testing Only)

**Step 1:** Open Windows Security
- Search for "Windows Defender Firewall" and open it

**Step 2:** Turn off temporarily
- Click **Turn Windows Defender Firewall on or off**
- Select **Turn off for Private networks**
- Click **OK**

**Test connection in container:**
```bash
export OLLAMA_API_URL="http://192.168.29.30:11434"
python scripts/test_setup.py
```

⚠️ **Remember to turn firewall back ON after testing!**

---

### Option 3: Configure Ollama as Inbound Rule

**Step 1:** Open Windows Defender Firewall with Advanced Security
- Press `Win + R`
- Type: `wf.msc`
- Press Enter

**Step 2:** Create Inbound Rule
- Click **Inbound Rules** (left panel)
- Click **New Rule** (right panel)
- Select **Port** → **Next**
- Select **TCP** and enter port: `11434`
- Select **Allow the connection**
- Apply to: Private networks (recommended)
- Name it: "Ollama LLM"
- Click **Finish**

---

## Verify Firewall Fix

After allowing Ollama through the firewall:

**From Windows PowerShell:**
```powershell
curl http://localhost:11434/api/tags -UseBasicParsing
```

Should return JSON with model info.

**From Container:**
```bash
cd /workspaces/USSOregon
source venv/bin/activate
export OLLAMA_API_URL="http://192.168.29.30:11434"
python scripts/test_setup.py
```

Should show: `✅ Ollama is running!`

---

## Alternative: Use Docker Network Bridge

If firewall issues persist, try connecting via Docker's host gateway:

```bash
export OLLAMA_API_URL="http://host.docker.internal:11434"
python scripts/test_setup.py
```

---

## Verify Ollama Configuration

Make sure Ollama is still configured to listen on all interfaces:

**On Windows PowerShell:**
```powershell
# Check environment variable
[Environment]::GetEnvironmentVariable("OLLAMA_HOST", "User")
# Should output: 0.0.0.0:11434

# Check running process
Get-Process ollama
```

---

## Summary

1. ✅ **Most likely:** Windows Firewall is blocking port 11434
2. ✅ **Solution:** Allow Ollama through firewall (Option 1 recommended)
3. ✅ **Verify:** Run test_setup.py after allowing firewall
4. ✅ **Test:** Run demo to see real LLM responses

Once firewall is fixed, you'll have full Teddy AI working! 🚀
