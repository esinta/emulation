# ============================================================================
# ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY
#
# Makefile for BadDownloader Stage 1
# Cross-compiles from macOS/Linux using mingw-w64
#
# Prerequisites:
#   macOS:  brew install mingw-w64
#   Ubuntu: apt install mingw-w64
#   Fedora: dnf install mingw64-gcc
#
# Usage:
#   make        - Build the exe
#   make clean  - Remove build artifacts
# ============================================================================

# Cross-compiler for 64-bit Windows
CC = x86_64-w64-mingw32-gcc

# Compiler flags
#   -Wall           : Enable all warnings
#   -Wextra         : Extra warnings
#   -mconsole       : Console subsystem (show stdout output)
CFLAGS = -Wall -Wextra -mconsole

# Output filename
TARGET = BadDownloader.exe

# Source files
SOURCES = downloader.c

# Default target
all: $(TARGET)

# Build the exe
$(TARGET): $(SOURCES)
	@echo "[*] Building BadDownloader..."
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCES)
	@echo "[*] Built: $(TARGET)"
	@ls -lh $(TARGET)

# Clean build artifacts
clean:
	@echo "[*] Cleaning build artifacts..."
	rm -f $(TARGET)
	@echo "[*] Clean complete"

.PHONY: all clean
