# MuddyCalc Lab Setup — LibreOffice Installation

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This code replicates documented malware behavior for defensive security
testing and endpoint telemetry validation. It does NOT contain real malware
payloads, exploits, or evasion techniques.

LEGAL: Only run this in environments you own or have explicit written
authorization to test. Unauthorized use may violate computer fraud laws.

Final payload: calc.exe (safe, benign)
C2: Local network only (hardcoded private IP: 192.168.0.148)
============================================================================
```

## Overview

MuddyCalc uses LibreOffice Calc as the document application on the Windows VM. This avoids requiring a Microsoft Office license for the lab environment.

## Step 1: Download LibreOffice

Download the Windows installer from https://www.libreoffice.org/download/download-libreoffice/

Select:
- **Operating System:** Windows (x86_64)
- **Format:** `.msi` installer

Alternatively, serve the installer from your MacBook:

```bash
# On MacBook — place the .msi in a convenient directory
cd ~/Downloads
python3 -m http.server 8888
```

```powershell
# On Windows VM — download the installer
Invoke-WebRequest -Uri "http://192.168.0.148:8888/LibreOffice_25.2.1_Win_x86-64.msi" -OutFile "$HOME\Downloads\LibreOffice.msi"
```

## Step 2: Install LibreOffice

1. Double-click the downloaded `.msi` file
2. Follow the installer wizard with default options
3. Select **Typical** installation when prompted
4. Complete the installation

## Step 3: Configure Macro Security

This is **critical** — macros will not execute unless security is set to Low.

1. Open **LibreOffice Calc**
2. Go to **Tools → Options** (or **Alt + F12**)
3. Navigate to **LibreOffice → Security**
4. Click **Macro Security...**
5. Select **Low** (Warn me before executing macros from untrusted sources)
6. Click **OK** to close all dialogs
7. **Restart LibreOffice** for the setting to take effect

## Step 4: Verify Macro Support

1. Open LibreOffice Calc
2. Go to **Tools → Macros → Organize Dialogs → BASIC**
3. Verify you can create a new module and enter code
4. Test with a simple macro:
   ```vba
   Sub TestMacro()
       MsgBox "Macros are working!"
   End Sub
   ```
5. Run the macro — you should see the message box

## Step 5: Verify COM Object Support

MuddyCalc's macro uses `CreateObject("WScript.Shell")` and `CreateObject("Scripting.FileSystemObject")`. Verify these work:

1. In LibreOffice Calc, go to **Tools → Macros → Organize Dialogs → BASIC**
2. Create a test macro:
   ```vba
   Sub TestCOM()
       Dim wsh As Object
       Set wsh = CreateObject("WScript.Shell")
       MsgBox "WScript.Shell works! TEMP = " & wsh.ExpandEnvironmentStrings("%TEMP%")
       Set wsh = Nothing
   End Sub
   ```
3. Run the macro — you should see a message box with your TEMP path

If this fails, ensure:
- You're running LibreOffice on Windows (COM objects are Windows-only)
- Macro security is set to Low
- LibreOffice was restarted after changing security settings

## Troubleshooting

### Macros don't execute
- Verify macro security is set to Low
- Restart LibreOffice after changing settings
- Check that the macro is in the document's Basic modules, not a global library

### CreateObject fails
- This only works on Windows — COM objects are not available on macOS/Linux
- Ensure the macro runs within LibreOffice on the Windows VM

### .xlsm format not available in Save As
- Make sure you're using a recent version of LibreOffice (7.x+)
- The format appears as "Microsoft Excel 2007-365 (.xlsm)" in the Save As dialog
- If not listed, check that the Microsoft file format filters are installed
