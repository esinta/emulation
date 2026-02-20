# ============================================================================
# ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY
#
# Makefile for JawDropper Stage 2 DLL
# Cross-compiles from macOS/Linux using mingw-w64
#
# Prerequisites:
#   macOS:  brew install mingw-w64
#   Ubuntu: apt install mingw-w64
#   Fedora: dnf install mingw64-gcc
#
# Usage:
#   make        - Build the DLL
#   make clean  - Remove build artifacts
# ============================================================================

# Cross-compiler for 64-bit Windows
CC = x86_64-w64-mingw32-gcc

# Compiler flags
#   -Wall           : Enable all warnings
#   -Wextra         : Extra warnings
#   -shared         : Build as shared library (DLL)
#   -mwindows       : Windows subsystem (no console)
CFLAGS = -Wall -Wextra -shared -mwindows

# Linker flags
#   -lwinhttp       : WinHTTP library for C2 beacon
#   -lole32         : OLE32 for COM types (HRESULT, etc.)
LDFLAGS = -lwinhttp -lole32

# Output filename
TARGET = jawdropper.dll

# Source files
SOURCES = loader.c
DEFFILE = loader.def

# Default target
all: $(TARGET)

# Build the DLL
$(TARGET): $(SOURCES) $(DEFFILE)
	@echo "[*] Building JawDropper DLL..."
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCES) $(DEFFILE) $(LDFLAGS)
	@echo "[*] Built: $(TARGET)"
	@ls -lh $(TARGET)

# Clean build artifacts
clean:
	@echo "[*] Cleaning build artifacts..."
	rm -f $(TARGET)
	@echo "[*] Clean complete"

# Install to payloads directory
install: $(TARGET)
	@echo "[*] Copying to c2-server/payloads/..."
	cp $(TARGET) ../c2-server/payloads/payload.dll
	@echo "[*] Installed as: ../c2-server/payloads/payload.dll"

# Phony targets
.PHONY: all clean install
