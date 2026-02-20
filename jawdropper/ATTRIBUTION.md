# JawDropper Attribution

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This document maps each component of JawDropper to its public source
documentation. Every technique implemented is already publicly documented.
============================================================================
```

This document maps every technique and behavior in JawDropper to publicly available documentation. We don't implement novel offensive capabilities — we reconstruct what's already known.

## Primary Sources

### CISA Advisory AA23-242A
**Title:** Identification and Disruption of QakBot Infrastructure
**Date:** August 30, 2023
**URL:** https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-242a

This advisory documents QakBot's TTPs following the FBI's Operation "Duck Hunt" takedown. It describes:
- Initial access via phishing with malicious attachments
- Use of JavaScript files for execution
- PowerShell download cradles
- DLL execution via regsvr32
- Discovery command patterns
- Persistence mechanisms

### MITRE ATT&CK: QakBot (S0650)
**URL:** https://attack.mitre.org/software/S0650/

MITRE's documentation of QakBot techniques, referenced for each component below.

### pr0xylife QakBot IOC Repository
**URL:** https://github.com/pr0xylife/Qakbot

Community-maintained repository tracking QakBot campaigns, including BB27 and BB28 campaigns from May 2023 that JawDropper emulates.

### The DFIR Report
**URL:** https://thedfirreport.com/

Multiple case studies documenting real-world QakBot intrusions with detailed process trees and command patterns.

---

## Component Attribution

### Stage 1: JavaScript Dropper (`dropper.js`)

| Element | Source | Reference |
|---------|--------|-----------|
| JS file delivery via phishing | CISA AA23-242A | "QakBot is commonly spread through phishing emails containing malicious attachments or links" |
| wscript.exe execution | MITRE T1059.007 | QakBot documented using JavaScript for initial execution |
| Base64-encoded PowerShell | CISA AA23-242A | "PowerShell commands... often encoded to evade detection" |
| Hidden window execution | MITRE T1059.001 | Standard PowerShell download cradle technique |

**BB27/BB28 Campaign Specifics:**
- The May 2023 QakBot campaigns (tracked as BB27 and BB28 by pr0xylife) used .js files distributed via reply-chain phishing emails
- Campaign IDs observed in pr0xylife repository: `bb27` and `bb28`
- Distribution method: ZIP files containing JS files

### Stage 2: PowerShell Download Cradle

| Element | Source | Reference |
|---------|--------|-----------|
| Invoke-WebRequest / WebClient | CISA AA23-242A | Standard PowerShell download techniques |
| Download to %TEMP% | MITRE T1105 | Ingress tool transfer to temp directories |
| regsvr32 execution | CISA AA23-242A | "loads QakBot DLL using regsvr32.exe" |

**Command Pattern:**
The download → execute pattern (`Invoke-WebRequest` followed by `regsvr32 /s`) is documented in multiple DFIR Report case studies of QakBot infections.

### Stage 3: DLL Loader (`loader.c`)

#### Anti-Analysis Delay
| Element | Source | Reference |
|---------|--------|-----------|
| Sleep before execution | MITRE T1497.003 | Time-Based Evasion |
| 2-second delay | DFIR Report | Observed in QakBot DLL behavior |

**Note:** Real QakBot uses more sophisticated time-based evasion. We implement only the basic sleep as documented.

#### Discovery Commands

| Command | Technique | Source |
|---------|-----------|--------|
| `whoami` | T1033 | CISA AA23-242A: "system and user discovery" |
| `ipconfig /all` | T1016 | CISA AA23-242A: "network configuration discovery" |
| `net view` | T1018 | MITRE S0650: Remote System Discovery |
| `arp -a` | T1016 | DFIR Report: Network reconnaissance |
| `nslookup _ldap._tcp.dc._msdcs.%USERDNSDOMAIN%` | T1018 | CISA AA23-242A: Domain controller enumeration |
| `nltest /domain_trusts /all_trusts` | T1482 | CISA AA23-242A: Domain trust discovery |

**Discovery Pattern:**
The DFIR Report documents QakBot performing a "discovery burst" of system commands shortly after execution. The specific commands above are compiled from multiple public sources documenting QakBot reconnaissance behavior.

#### Persistence: Scheduled Task

| Element | Source | Reference |
|---------|--------|-----------|
| schtasks /create | MITRE T1053.005 | Scheduled Task/Job |
| Daily trigger | CISA AA23-242A | QakBot persistence mechanisms |

**Safety Modification:**
Real QakBot creates a scheduled task that runs `regsvr32` with the malicious DLL. JawDropper creates a scheduled task for `calc.exe` instead — providing the same telemetry signature without risk.

#### C2 Beacon

| Element | Source | Reference |
|---------|--------|-----------|
| HTTP POST beacon | MITRE T1071.001 | Application Layer Protocol: Web |
| JSON payload | DFIR Report | QakBot C2 communication patterns |
| Hostname/PID reporting | CISA AA23-242A | System information exfiltration |

**Safety Modification:**
Real QakBot beacons to attacker-controlled infrastructure with encrypted payloads. JawDropper beacons to a local private IP with plaintext JSON.

### Execution Flow: regsvr32

| Element | Source | Reference |
|---------|--------|-----------|
| regsvr32.exe /s | MITRE T1218.010 | Signed Binary Proxy Execution |
| DllRegisterServer export | CISA AA23-242A | QakBot DLL execution method |
| Silent flag (/s) | DFIR Report | Suppresses dialog boxes |

---

## What We Don't Emulate

The following QakBot behaviors are NOT implemented because they cross the line from emulation to weaponization:

| Behavior | Why Not Implemented |
|----------|---------------------|
| Process injection (wermgr.exe, explorer.exe) | Could hide malicious activity; not needed for TTP emulation |
| Credential harvesting | Actual credential theft capability |
| Email harvesting | Privacy violation, data exfiltration |
| Code signing evasion | Helps attackers, not defenders |
| Encrypted C2 communications | Obfuscation, not useful for detection testing |
| Module download and execution | Would require real payload delivery |
| Lateral movement | Requires network access beyond lab |

---

## Technique ID Cross-Reference

| MITRE ID | Name | JawDropper Component |
|----------|------|---------------------|
| T1204.002 | User Execution: Malicious File | dropper.js execution |
| T1059.007 | Command & Scripting: JavaScript | dropper.js via wscript.exe |
| T1059.001 | Command & Scripting: PowerShell | Download cradle |
| T1105 | Ingress Tool Transfer | DLL download |
| T1218.010 | Signed Binary Proxy: Regsvr32 | DLL loading |
| T1497.003 | Time-Based Evasion | Sleep(2000) |
| T1033 | System Owner/User Discovery | whoami |
| T1016 | System Network Config Discovery | ipconfig, arp |
| T1018 | Remote System Discovery | net view, nslookup |
| T1482 | Domain Trust Discovery | nltest |
| T1053.005 | Scheduled Task/Job | schtasks /create |
| T1071.001 | Application Layer Protocol: Web | HTTP beacon |

---

## External References

1. **CISA Advisory AA23-242A**
   https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-242a

2. **MITRE ATT&CK: QakBot (S0650)**
   https://attack.mitre.org/software/S0650/

3. **pr0xylife QakBot Repository**
   https://github.com/pr0xylife/Qakbot

4. **The DFIR Report: QakBot Leads to Cobalt Strike**
   https://thedfirreport.com/2022/02/07/qbot-likes-to-move-it-move-it/

5. **Elastic Security: QakBot Malware Analysis**
   https://www.elastic.co/security-labs/qakbot-malware-analysis

6. **Red Canary: QakBot Threat Report**
   https://redcanary.com/threat-detection-report/threats/qbot/

7. **Splunk: QakBot Detection**
   https://www.splunk.com/en_us/blog/security/qakbot-detection.html
