# BadDownloader — Attribution & Intelligence Sources

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

## About This Emulation

BadDownloader is a **synthetic emulation** — it is not based on a specific CISA advisory or named threat actor campaign. It represents common "script kiddie" downloader behavior observed across thousands of commodity malware samples.

The techniques individually map to real-world campaigns, but the specific chain is constructed for educational purposes to demonstrate that even basic, unsophisticated threats leave detectable traces in endpoint telemetry.

## Why a Synthetic Emulation?

The first two Esinta emulations (JawDropper and MuddyCalc) reconstruct specific, documented APT campaigns. BadDownloader intentionally takes the opposite approach — a generic, unsophisticated downloader — to illustrate that:

1. **Simple threats are detectable.** You don't need a named APT to test your detection pipeline.
2. **Process trees tell a story.** Even a basic `exe → cmd.exe → powershell.exe` chain is anomalous.
3. **Discovery bursts are universal.** Whether it's QakBot, MuddyWater, or a script kiddie, attackers run `whoami` and `ipconfig`.

## Technique Attribution

Each technique used in BadDownloader is documented in MITRE ATT&CK and observed in real-world malware campaigns.

### Stage 1: Download Cradle

| Technique | MITRE ID | MITRE ATT&CK URL | Real-World Usage |
|-----------|----------|-------------------|------------------|
| PowerShell | T1059.001 | https://attack.mitre.org/techniques/T1059/001/ | Used by virtually all commodity malware and APT groups for download cradles |
| Ingress Tool Transfer | T1105 | https://attack.mitre.org/techniques/T1105/ | HTTP-based payload downloads are the most common delivery mechanism |
| Windows Command Shell | T1059.003 | https://attack.mitre.org/techniques/T1059/003/ | cmd.exe as intermediary is standard for batch-based downloaders |

### Stage 2: Discovery

| Technique | MITRE ID | MITRE ATT&CK URL | Real-World Usage |
|-----------|----------|-------------------|------------------|
| System Owner/User Discovery | T1033 | https://attack.mitre.org/techniques/T1033/ | `whoami` is the single most common post-exploitation command |
| System Network Configuration | T1016 | https://attack.mitre.org/techniques/T1016/ | `ipconfig /all` for network enumeration — used by QakBot, Emotet, TrickBot |
| System Information Discovery | T1082 | https://attack.mitre.org/techniques/T1082/ | `systeminfo` for OS fingerprinting — used across commodity and APT malware |
| Local Account Discovery | T1087.001 | https://attack.mitre.org/techniques/T1087/001/ | `net user` for account enumeration — common in post-exploitation frameworks |

### Stage 2: Persistence

| Technique | MITRE ID | MITRE ATT&CK URL | Real-World Usage |
|-----------|----------|-------------------|------------------|
| Scheduled Task | T1053.005 | https://attack.mitre.org/techniques/T1053/005/ | `schtasks /create` for persistence — used by QakBot, Emotet, Cobalt Strike |

### Delivery

| Technique | MITRE ID | MITRE ATT&CK URL | Real-World Usage |
|-----------|----------|-------------------|------------------|
| User Execution: Malicious File | T1204.002 | https://attack.mitre.org/techniques/T1204/002/ | Direct execution of malicious binaries — the most basic delivery vector |

## References

- [MITRE ATT&CK](https://attack.mitre.org/) — Adversarial Tactics, Techniques, and Common Knowledge
- [MITRE ATT&CK: PowerShell (T1059.001)](https://attack.mitre.org/techniques/T1059/001/)
- [MITRE ATT&CK: Windows Command Shell (T1059.003)](https://attack.mitre.org/techniques/T1059/003/)
- [MITRE ATT&CK: Ingress Tool Transfer (T1105)](https://attack.mitre.org/techniques/T1105/)
- [MITRE ATT&CK: System Information Discovery (T1082)](https://attack.mitre.org/techniques/T1082/)
- [MITRE ATT&CK: Scheduled Task (T1053.005)](https://attack.mitre.org/techniques/T1053/005/)
