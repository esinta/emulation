# Esinta Emulation — Safety Philosophy

This document explains the safety mechanisms built into every emulation in this repository. These are non-negotiable requirements for all contributions.

## Core Principles

### 1. Safe Payloads

**The final payload is ALWAYS `calc.exe` or another obviously benign process.**

This is a hardcoded value in the source code. It is NOT:
- Configurable via command-line arguments
- Configurable via environment variables
- Configurable via configuration files
- Configurable via C2 server responses

Anyone who wants to change the payload must deliberately modify and recompile the source code. This creates a clear line between "using the tool as designed" and "modifying it for other purposes."

Why `calc.exe`?
- It's universally present on Windows systems
- It's obviously benign — no reasonable person could mistake it for a real payload
- It's visually distinctive — you immediately know the emulation succeeded
- It's the industry standard for proof-of-concept demonstrations

### 2. No Evasion Techniques

**Code is intentionally NOT obfuscated.**

Every emulation in this repository includes:
- Clear, readable code with descriptive variable names
- Extensive comments explaining what each section does
- MITRE ATT&CK technique IDs mapped to specific code blocks
- References to the public documentation being emulated

We do NOT include:
- String encryption or obfuscation
- API hashing or dynamic resolution
- Anti-debugging checks (beyond simple timing as documented in the original malware)
- Sandbox evasion beyond what's documented in public advisories
- Process injection techniques that hide execution
- Code signing or timestomping

The goal is education, not evasion. If a security tool can't detect these emulations, that's useful information — but we're not trying to help evade detection.

### 3. No Exploits

**We emulate post-exploitation behavior, not initial exploitation.**

This repository does NOT contain:
- CVE exploits
- Zero-day vulnerabilities
- Buffer overflows, use-after-free, or other memory corruption
- Privilege escalation exploits
- Authentication bypasses
- Any code designed to gain unauthorized access

We emulate what malware does AFTER it's already running. The "initial access" in our emulations is always "user executes a file" — the same as double-clicking a document.

### 4. Local C2 Only

**C2 addresses are hardcoded private RFC1918 IP addresses.**

Every emulation that includes C2 communication:
- Uses a hardcoded private IP address (e.g., `192.168.0.148`)
- Does NOT accept C2 addresses as command-line arguments
- Does NOT read C2 addresses from configuration files
- Does NOT resolve C2 addresses via DNS

The C2 server runs on the tester's local network, typically on their development machine. These emulations will not connect to public internet infrastructure.

Private IP ranges used:
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

### 5. Prominent Disclaimers

Every source file includes the standard header:

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This code replicates documented malware behavior for defensive security
testing and endpoint telemetry validation. It does NOT contain real malware
payloads, exploits, or evasion techniques.

LEGAL: Only run this in environments you own or have explicit written
authorization to test. Unauthorized use may violate computer fraud laws.

Final payload: calc.exe (safe, benign)
C2: Local network only (hardcoded private IP)
============================================================================
```

This disclaimer appears in:
- Every README.md file
- Every source code file header
- The repository root README
- The license file

## What We Emulate vs. What We Don't

### We DO Emulate

| Category | Examples | Why |
|----------|----------|-----|
| Process trees | wscript → powershell → regsvr32 | Validates process-based detection |
| Discovery commands | whoami, ipconfig, net view | Tests command-line logging |
| Persistence mechanisms | Scheduled tasks (with safe payloads) | Validates persistence detection |
| C2 beaconing patterns | HTTP POST to local server | Tests network telemetry |
| Execution techniques | regsvr32 DLL loading | Tests signed binary proxy detection |

### We DON'T Emulate

| Category | Examples | Why Not |
|----------|----------|---------|
| Real payloads | Ransomware, RATs, miners | Dangerous, no legitimate testing need |
| Exploits | CVEs, buffer overflows | Could enable unauthorized access |
| Evasion | API hashing, string encryption | Helps attackers, not defenders |
| Credential theft | Mimikatz, LSASS dumping | Too easily weaponized |
| Lateral movement | Pass-the-hash, remote execution | Requires real credentials |
| Data exfiltration | Actual file theft | No legitimate testing need |

## Responsible Use

### Authorized Environments Only

These emulations should ONLY be used in:
- Lab environments you own
- Systems with explicit written authorization from the owner
- Isolated virtual machines with no network access to production
- Controlled testing environments with proper change management

### Pre-Execution Checklist

Before running any emulation:
1. ☐ Confirm you have authorization (written if required by your org)
2. ☐ Snapshot your test VM so you can revert
3. ☐ Disable or isolate network connections to production
4. ☐ Inform your SOC/security team if applicable
5. ☐ Document your testing for audit purposes

### Post-Execution Cleanup

After running any emulation:
1. ☐ Remove any scheduled tasks created
2. ☐ Delete any downloaded files
3. ☐ Revert to VM snapshot if available
4. ☐ Document results for your records

## Responsible Disclosure

If you discover a way to weaponize this code beyond its intended scope — for example, a technique that could be modified to bypass the safety mechanisms — please contact us:

**security@esinta.com**

We take responsible disclosure seriously and will work with you to address any concerns.

## Modifications and Forks

If you fork this repository and remove safety mechanisms:
- You are solely responsible for any consequences
- You may not use the Esinta name or branding
- You should clearly indicate that your fork is modified
- Consider whether your modifications could enable harm

We encourage forks that ADD safety mechanisms, improve documentation, or extend emulations in ways consistent with this philosophy.

## Questions?

If you have questions about whether a particular use case is appropriate, contact us at hello@esinta.com. We're happy to discuss.
