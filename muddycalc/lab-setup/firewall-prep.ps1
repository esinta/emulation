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
# MuddyCalc Lab Firewall Configuration
#
# Configures Windows Firewall on the test VM to:
#   - Block all outbound traffic by default
#   - Allow connections to Esinta Endpoints server (192.168.0.113:443)
#   - Allow connections to MacBook C2 server (192.168.0.148:8888)
#
# Run as Administrator:
#   powershell.exe -ExecutionPolicy Bypass -File firewall-prep.ps1
#
# To remove these rules later:
#   Get-NetFirewallRule -DisplayName "Esinta Lab*" | Remove-NetFirewallRule
# ============================================================================

# Block all outbound by default
New-NetFirewallRule -DisplayName "Esinta Lab - Block All Outbound" `
    -Direction Outbound -Action Block -Profile Any -Enabled True

# Allow Esinta Endpoints server
New-NetFirewallRule -DisplayName "Esinta Lab - Esinta Server (Outbound)" `
    -Direction Outbound -Action Allow -Protocol TCP `
    -RemoteAddress 192.168.0.113 -RemotePort 443 `
    -Profile Any -Enabled True

# Allow MacBook C2 server
New-NetFirewallRule -DisplayName "Esinta Lab - MacBook C2 (Outbound)" `
    -Direction Outbound -Action Allow -Protocol TCP `
    -RemoteAddress 192.168.0.148 -RemotePort 8888 `
    -Profile Any -Enabled True

Write-Host ""
Write-Host "Firewall rules configured:" -ForegroundColor Green
Write-Host "  [BLOCK] All outbound traffic (default deny)"
Write-Host "  [ALLOW] 192.168.0.113:443  (Esinta Endpoints server)"
Write-Host "  [ALLOW] 192.168.0.148:8888 (MacBook C2 server)"
Write-Host ""
Write-Host "To verify:" -ForegroundColor Yellow
Write-Host '  Get-NetFirewallRule -DisplayName "Esinta Lab*" | Format-Table DisplayName, Action, Direction'
Write-Host ""
Write-Host "To remove all lab rules:" -ForegroundColor Yellow
Write-Host '  Get-NetFirewallRule -DisplayName "Esinta Lab*" | Remove-NetFirewallRule'
