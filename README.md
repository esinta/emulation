# Esinta Emulation

Malware behavior emulation samples for defensive security testing and endpoint telemetry validation.

Built by [Esinta](https://esinta.com) for the OT/ICS security community.

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This repository contains code that replicates documented malware behavior
for defensive security testing and endpoint telemetry validation. It does
NOT contain real malware payloads, exploits, or evasion techniques.

LEGAL: Only run this in environments you own or have explicit written
authorization to test. Unauthorized use may violate computer fraud laws.

Final payloads: calc.exe (safe, benign)
C2: Local network only (hardcoded private IPs)
============================================================================
```

## Purpose

This repository helps security teams validate their detection capabilities by providing safe, documented malware behavior emulations. Each emulation replicates the exact TTP chain of real-world malware campaigns, but with:

- **Safe payloads** — Final payload is always `calc.exe` or another obviously benign process
- **Local C2** — C2 servers use hardcoded private RFC1918 IP addresses
- **Full transparency** — No obfuscation, extensive comments explaining each step

These emulations are designed for:
- Validating endpoint detection and response (EDR) tools
- Testing SIEM correlation rules
- Training SOC analysts on real attack patterns
- Creating video demonstrations of attack chains
- Verifying telemetry collection in lab environments

## Philosophy

We emulate **techniques**, not **exploits**.

Every behavior in this repo is already publicly documented in CISA advisories, MITRE ATT&CK, and vendor threat reports. We don't ship novel offensive capabilities — we reconstruct what's already known so defenders can test against it.

Key principles:
1. **Attribution first** — Every technique maps to a public source (CISA, MITRE, vendor reports)
2. **Safety by design** — Safe payloads and local C2 are hardcoded, not configurable
3. **Education over evasion** — Code is intentionally readable with extensive comments
4. **Defense-focused** — Built for blue teams, not red teams

## Available Emulations

| Name | Malware Family | Reference | Primary Techniques | Status |
|------|---------------|-----------|-------------------|--------|
| [JawDropper](jawdropper/) | QakBot (Qakbot/Pinkslipbot) | [CISA AA23-242A](https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-242a) | T1059.001, T1218.010, T1082, T1053.005 | ✅ Available |

## Safety Mechanisms

All emulations implement two critical safety layers:

### 1. Hardcoded Safe Payload
The final payload is ALWAYS `calc.exe`. This is hardcoded in source code and cannot be changed via command-line arguments or configuration files. Someone forking this repo would have to deliberately modify and recompile the source code to change the payload.

### 2. Local-Only C2
C2 servers run on private RFC1918 IP addresses (e.g., `192.168.0.148`). These addresses are hardcoded in the source code. The emulations will not connect to public internet infrastructure.

See [SAFETY.md](SAFETY.md) for our complete safety philosophy.

## Quick Start: JawDropper

### Prerequisites
- macOS or Linux development machine with `mingw-w64` installed
- Windows VM for execution (isolated, snapshotted)
- Python 3.x on the development machine

### Setup

1. **Build the Stage 2 DLL** (on your Mac/Linux):
   ```bash
   cd jawdropper/stage2-loader
   ./build.sh
   ```

2. **Start the C2 server** (on your Mac at 192.168.0.148):
   ```bash
   # Simple approach:
   cd jawdropper && python3 -m http.server 8888

   # Or with beacon logging:
   python3 jawdropper/c2-server/server.py --port 8888
   ```

3. **Copy dropper.js to the Windows VM**

4. **Execute on the Windows VM**:
   - Double-click `dropper.js`
   - Watch the process tree in your endpoint telemetry tool
   - Observe `calc.exe` launch as the final "payload"

### Expected Process Tree
```
wscript.exe dropper.js
  └── powershell.exe -encodedcommand ...
        └── regsvr32.exe /s update.dll
              ├── cmd.exe /c whoami
              ├── cmd.exe /c ipconfig /all
              ├── cmd.exe /c net view
              ├── cmd.exe /c arp -a
              ├── cmd.exe /c nslookup ...
              ├── cmd.exe /c nltest ...
              ├── cmd.exe /c schtasks ...
              └── calc.exe
```

## Contributing

Want to add a new malware emulation? Use the `_template/` folder as a starting point:

1. Copy `_template/` to a new folder named after your emulation
2. Fill in the README.md with malware family details
3. Complete ATTRIBUTION.md with all public source references
4. Implement the emulation following our safety requirements
5. Test thoroughly in an isolated environment
6. Submit a pull request

All contributions must:
- Map every technique to a public source (CISA, MITRE, vendor reports)
- Use safe payloads (calc.exe or equivalent)
- Use local/private C2 addresses only
- Include comprehensive documentation

## Legal Disclaimer

**This software is provided for authorized security testing and educational purposes only.**

By using this software, you agree that:
- You will only use it in environments you own or have explicit written authorization to test
- You understand that unauthorized use may violate local, state, federal, or international computer fraud and abuse laws
- The authors and contributors are not responsible for any misuse or damage caused by this software
- You will not use this software for malicious purposes

This repository does not contain:
- Real malware payloads
- Exploits for vulnerabilities
- Evasion techniques designed to bypass security controls
- Code designed for unauthorized access

## Related Projects

- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) — Library of tests mapped to MITRE ATT&CK
- [MITRE Caldera](https://github.com/mitre/caldera) — Automated adversary emulation platform
- [Esinta Endpoints](https://esinta.com) — OT/ICS endpoint visibility

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

## Contact

- Security concerns: security@esinta.com
- General inquiries: hello@esinta.com
