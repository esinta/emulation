# MuddyCalc — Attribution & Intelligence Sources

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

## Threat Actor: MuddyWater

| Attribute | Detail |
|-----------|--------|
| **Names** | MuddyWater, MERCURY, Mango Sandstorm, Seedworm, TEMP.Zagros, Static Kitten |
| **MITRE ID** | [G0069](https://attack.mitre.org/groups/G0069/) |
| **Sponsor** | Iran Ministry of Intelligence and Security (MOIS) |
| **Active Since** | At least 2017 |
| **Targets** | Government, defense, oil & gas, telecoms, IT — Middle East, North America, Europe, Asia |

## Primary References

| Source | Title | Relevance |
|--------|-------|-----------|
| CISA | [AA22-055A: Iranian Government-Sponsored Actors Conduct Cyber Operations](https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-055a) | Primary advisory — documents MuddyWater TTPs including macro delivery, PowerShell backdoors, and registry persistence |
| MITRE ATT&CK | [G0069 — MuddyWater](https://attack.mitre.org/groups/G0069/) | Comprehensive technique mapping for the group |
| MITRE ATT&CK | [S0223 — POWERSTATS](https://attack.mitre.org/software/S0223/) | Malware profile for the PowerShell backdoor |

## Component Attribution

### Stage 1: Macro-Enabled Spreadsheet

| Technique | MITRE ID | Source |
|-----------|----------|--------|
| Spearphishing Attachment | T1566.001 | CISA AA22-055A: "MuddyWater actors are known to exploit publicly reported vulnerabilities and use open-source tools and strategies to gain access to sensitive data on victims' systems and deploy ransomware. These actors also maintain persistence on victim networks via tactics such as side-loading DLLs and obfuscating PowerShell scripts." |
| User Execution: Malicious File | T1204.002 | Trend Micro: MuddyWater campaigns use macro-enabled documents with social engineering lures (invoices, government documents, reports) |
| VBScript Execution | T1059.005 | Unit 42 "Muddying the Water" (Nov 2017): Macros drop VBScript and other script files to %TEMP% for execution |

**Emulation notes:**
- Real MuddyWater uses spearphishing emails with attached macro-enabled documents
- Document lures include government correspondence, invoices, and internal reports
- We use an expense report lure — realistic corporate document
- Macro drops a VBScript to `%TEMP%`, matching observed MuddyWater behavior

### Stage 2: VBScript Persistence

| Technique | MITRE ID | Source |
|-----------|----------|--------|
| Registry Run Keys | T1547.001 | MITRE G0069: "MuddyWater has added Registry Run key entries for persistence" |
| VBScript Execution | T1059.005 | CISA AA22-055A: MuddyWater uses VBScript and JavaScript files dropped by macros |

**Emulation notes:**
- Real MuddyWater drops .dll + .reg files for persistence and payload staging
- We simplify to a single .vbs that handles both persistence and PowerShell launch
- **Safety:** Registry Run key value is `calc.exe`, not the backdoor
- Real MuddyWater Run key would point to a backdoor loader or script

### Stage 3: POWERSTATS Backdoor

| Technique | MITRE ID | Source |
|-----------|----------|--------|
| PowerShell | T1059.001 | MITRE S0223: "POWERSTATS is a PowerShell-based first stage backdoor" |
| Time-Based Evasion | T1497.003 | MITRE S0223: POWERSTATS includes sandbox detection via WMI queries |
| System Owner Discovery | T1033 | MITRE S0223: "POWERSTATS has the ability to identify the username on the compromised host" |
| System Information Discovery | T1082 | MITRE S0223: "POWERSTATS can retrieve the OS version, System info using systeminfo" |
| Network Configuration Discovery | T1016 | MITRE S0223: "POWERSTATS can identify network configuration information" |
| Process Discovery | T1057 | Symantec Seedworm report: Post-exploitation discovery includes running process enumeration |
| Domain Groups Discovery | T1069.002 | CISA AA22-055A: MuddyWater enumerates domain admin accounts for privilege escalation |
| File and Directory Discovery | T1083 | MITRE S0223: "POWERSTATS has the ability to find files of interest" |
| Web Protocols | T1071.001 | MITRE S0223: "POWERSTATS can use HTTP for C2 communication" |

**Emulation notes:**
- Real POWERSTATS uses multiple layers of obfuscation (base64, string replacement, encryption)
- Real POWERSTATS communicates over HTTPS to compromised web servers or cloud storage (OneDrive)
- We use plaintext HTTP to a local server
- Real POWERSTATS enters a C2 loop waiting for commands; we execute once and exit
- Discovery commands match those documented in CISA AA22-055A and MITRE S0223

## Vendor Reports Referenced

| Vendor | Report | Key Findings Used |
|--------|--------|-------------------|
| Unit 42 (Palo Alto) | "Muddying the Water: Targeted Attacks in the Middle East" (Nov 2017) | Initial POWERSTATS analysis, macro delivery chain, VBScript drop technique |
| Trend Micro | "MuddyWater Campaign Uses Decoy Documents to Deliver POWERSTATS Backdoor" | Detailed macro analysis, social engineering lure types, %TEMP% drop behavior |
| Symantec | "Seedworm: Group Compromises Government Agencies, Oil & Gas, NGOs, Telecoms, and IT Firms" | Post-exploitation discovery commands, persistence mechanisms |
| ClearSky | "MuddyWater Operations in Lebanon and Oman" | Target geography and sectors, C2 infrastructure patterns |
| Microsoft | "MERCURY leveraging Log4j 2 vulnerabilities" | Group attribution to MOIS, Mango Sandstorm naming |
| FireEye | "TEMP.Zagros (MuddyWater) Technical Analysis" | Detailed POWERSTATS reverse engineering, encoding schemes |

## What We Don't Emulate (and Why)

| Real Behavior | Reason Not Included |
|---------------|---------------------|
| Base52 string encoding | Evasion technique — not needed for detection validation |
| Multi-layer base64 obfuscation | Evasion technique — adds complexity without detection value |
| WMI sandbox detection | Evasion technique — we simplify to Start-Sleep |
| Encrypted C2 over HTTPS | Obfuscation — plaintext HTTP provides same telemetry signals |
| OneDrive/SharePoint C2 | Requires real cloud infrastructure; local HTTP is sufficient |
| Mimikatz/LaZagne credential dump | Actual offensive capability — not appropriate for emulation |
| Lateral movement (PsExec, WMI) | Could cause real damage in network environments |
| DLL side-loading | Requires specific vulnerable applications |
| POWERSTATS C2 loop with backoff | Would require manual cleanup and creates persistence risk |
