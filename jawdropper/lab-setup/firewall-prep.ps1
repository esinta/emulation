# ============================================================================
# ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY
#
# Firewall configuration script for JawDropper lab testing.
# Creates rules to allow communication with the C2 server.
#
# Usage: Run as Administrator
#   .\firewall-prep.ps1
# ============================================================================

#Requires -RunAsAdministrator

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "ESINTA EMULATION — Lab Firewall Configuration" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# C2 server configuration
$C2_IP = "192.168.0.148"
$C2_PORT = 8888

Write-Host "[*] Configuring firewall for JawDropper testing..." -ForegroundColor Yellow
Write-Host "    C2 Server: $C2_IP`:$C2_PORT" -ForegroundColor Gray
Write-Host ""

# Create outbound rule for C2 communication
$ruleName = "JawDropper-C2-Outbound"

# Check if rule already exists
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if ($existingRule) {
    Write-Host "[*] Rule '$ruleName' already exists. Removing and recreating..." -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName $ruleName
}

# Create new rule
New-NetFirewallRule `
    -DisplayName $ruleName `
    -Description "Allow JawDropper C2 communication to MacBook lab server" `
    -Direction Outbound `
    -Protocol TCP `
    -RemoteAddress $C2_IP `
    -RemotePort $C2_PORT `
    -Action Allow `
    -Profile Any `
    | Out-Null

Write-Host "[+] Created outbound rule: $ruleName" -ForegroundColor Green

# Create inbound rule (in case C2 needs to push data)
$inboundRuleName = "JawDropper-C2-Inbound"

$existingInbound = Get-NetFirewallRule -DisplayName $inboundRuleName -ErrorAction SilentlyContinue

if ($existingInbound) {
    Remove-NetFirewallRule -DisplayName $inboundRuleName
}

New-NetFirewallRule `
    -DisplayName $inboundRuleName `
    -Description "Allow inbound from JawDropper C2 server" `
    -Direction Inbound `
    -Protocol TCP `
    -RemoteAddress $C2_IP `
    -LocalPort Any `
    -Action Allow `
    -Profile Any `
    | Out-Null

Write-Host "[+] Created inbound rule: $inboundRuleName" -ForegroundColor Green

# Verify connectivity
Write-Host ""
Write-Host "[*] Testing connectivity to C2 server..." -ForegroundColor Yellow

try {
    $testConnection = Test-NetConnection -ComputerName $C2_IP -Port $C2_PORT -WarningAction SilentlyContinue

    if ($testConnection.TcpTestSucceeded) {
        Write-Host "[+] Connection to $C2_IP`:$C2_PORT successful!" -ForegroundColor Green
    } else {
        Write-Host "[-] Connection to $C2_IP`:$C2_PORT failed." -ForegroundColor Red
        Write-Host "    Make sure the C2 server is running:" -ForegroundColor Yellow
        Write-Host "    python3 -m http.server $C2_PORT" -ForegroundColor Gray
    }
} catch {
    Write-Host "[-] Could not test connection: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Firewall configuration complete." -ForegroundColor Cyan
Write-Host ""
Write-Host "To remove these rules after testing:" -ForegroundColor Yellow
Write-Host "  Remove-NetFirewallRule -DisplayName 'JawDropper-C2-Outbound'" -ForegroundColor Gray
Write-Host "  Remove-NetFirewallRule -DisplayName 'JawDropper-C2-Inbound'" -ForegroundColor Gray
Write-Host "============================================================================" -ForegroundColor Cyan
