# ============================================================================
# ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY
#
# Temporarily disable Windows Defender for JawDropper testing.
# These settings revert on reboot.
#
# Usage: Run as Administrator
#   .\disable-defender.ps1
#
# WARNING: Only use this in isolated lab environments!
# ============================================================================

#Requires -RunAsAdministrator

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "ESINTA EMULATION — Disable Windows Defender" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "WARNING: This script disables security protections." -ForegroundColor Red
Write-Host "         Only use in isolated lab environments!" -ForegroundColor Red
Write-Host ""

# Prompt for confirmation
$confirm = Read-Host "Type 'YES' to continue"
if ($confirm -ne "YES") {
    Write-Host "Aborted." -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "[*] Disabling Windows Defender protections..." -ForegroundColor Yellow
Write-Host ""

# Check if Tamper Protection is enabled
$tamperProtection = (Get-MpComputerStatus).IsTamperProtected
if ($tamperProtection) {
    Write-Host "[!] Tamper Protection is ENABLED" -ForegroundColor Red
    Write-Host "    You must disable it manually in Windows Security settings:" -ForegroundColor Yellow
    Write-Host "    Windows Security > Virus & threat protection > Manage settings" -ForegroundColor Gray
    Write-Host "    > Tamper Protection > Off" -ForegroundColor Gray
    Write-Host ""
    Write-Host "    After disabling Tamper Protection, run this script again." -ForegroundColor Yellow
    exit
}

# Disable real-time protection
try {
    Set-MpPreference -DisableRealtimeMonitoring $true
    Write-Host "[+] Disabled: Real-time protection" -ForegroundColor Green
} catch {
    Write-Host "[-] Failed to disable real-time protection: $_" -ForegroundColor Red
}

# Disable behavior monitoring
try {
    Set-MpPreference -DisableBehaviorMonitoring $true
    Write-Host "[+] Disabled: Behavior monitoring" -ForegroundColor Green
} catch {
    Write-Host "[-] Failed to disable behavior monitoring: $_" -ForegroundColor Red
}

# Disable IOAV protection (scans downloaded files)
try {
    Set-MpPreference -DisableIOAVProtection $true
    Write-Host "[+] Disabled: IOAV protection (download scanning)" -ForegroundColor Green
} catch {
    Write-Host "[-] Failed to disable IOAV protection: $_" -ForegroundColor Red
}

# Disable script scanning
try {
    Set-MpPreference -DisableScriptScanning $true
    Write-Host "[+] Disabled: Script scanning" -ForegroundColor Green
} catch {
    Write-Host "[-] Failed to disable script scanning: $_" -ForegroundColor Red
}

# Add exclusion for TEMP folder
$tempPath = [System.IO.Path]::GetTempPath()
try {
    Add-MpPreference -ExclusionPath $tempPath
    Write-Host "[+] Added exclusion: $tempPath" -ForegroundColor Green
} catch {
    Write-Host "[-] Failed to add exclusion: $_" -ForegroundColor Red
}

# Add exclusion for common test locations
$testPaths = @(
    "C:\Users\$env:USERNAME\Desktop",
    "C:\Users\$env:USERNAME\Downloads",
    "C:\Test"
)

foreach ($path in $testPaths) {
    if (Test-Path $path) {
        try {
            Add-MpPreference -ExclusionPath $path
            Write-Host "[+] Added exclusion: $path" -ForegroundColor Green
        } catch {
            Write-Host "[-] Failed to add exclusion for $path" -ForegroundColor Red
        }
    }
}

# Disable automatic sample submission
try {
    Set-MpPreference -SubmitSamplesConsent 2  # Never send
    Write-Host "[+] Disabled: Automatic sample submission" -ForegroundColor Green
} catch {
    Write-Host "[-] Failed to disable sample submission: $_" -ForegroundColor Red
}

# Disable cloud protection
try {
    Set-MpPreference -MAPSReporting 0  # Disabled
    Write-Host "[+] Disabled: Cloud-delivered protection" -ForegroundColor Green
} catch {
    Write-Host "[-] Failed to disable cloud protection: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Windows Defender has been disabled for testing." -ForegroundColor Green
Write-Host ""
Write-Host "These settings will revert when you reboot." -ForegroundColor Yellow
Write-Host ""
Write-Host "To re-enable manually:" -ForegroundColor Yellow
Write-Host "  Set-MpPreference -DisableRealtimeMonitoring `$false" -ForegroundColor Gray
Write-Host "  Set-MpPreference -DisableBehaviorMonitoring `$false" -ForegroundColor Gray
Write-Host ""
Write-Host "Or simply reboot the VM." -ForegroundColor Yellow
Write-Host "============================================================================" -ForegroundColor Cyan

# Show current status
Write-Host ""
Write-Host "[*] Current Defender Status:" -ForegroundColor Yellow
Get-MpComputerStatus | Select-Object `
    RealTimeProtectionEnabled, `
    BehaviorMonitorEnabled, `
    IoavProtectionEnabled, `
    OnAccessProtectionEnabled | Format-List
