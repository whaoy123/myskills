---
name: national-instruments-clean-uninstall
description: Cleanly remove all National Instruments software, MAX/DAQmx configuration, residual files, and registry entries on Windows, then prepare a minimal cDAQ reinstallation. Use only when the user explicitly wants a full NI reset or clean reinstall.
---

# National Instruments Clean Uninstall

Use NI's clean-uninstall sequence. This is a destructive workflow: it removes NI software, MAX configuration, NI-DAQmx Tasks, Global Virtual Channels, custom scales, and related system state. It is not the right workflow for repairing one package or retaining an existing test setup.

## Establish scope and preserve wanted data

1. Confirm the user wants a full NI reset rather than targeted repair. State the affected configuration objects before changing anything.
2. Ask whether any MAX configuration needs exporting. In MAX 5.0 or newer, `Tools > Reset Configuration Data` resets the MAX database and requires a restart. It clears NI-DAQmx Tasks, Global Virtual Channels, custom scales, and device configuration, but not the physical hardware.
3. Identify user data separately from software residue. Do not delete FlexLogger projects, TDMS, CSV, or other acquisition data unless the user explicitly includes them.

## Uninstall in the required order

1. If MAX is still installed and its configuration should be reset, use `Tools > Reset Configuration Data`, then restart when prompted.
2. Run NI Package Manager as administrator. In **Installed**, open the settings gear, enable **Show full version numbers and hidden packages**, disable **Products only**, then remove every listed NI package.
3. Only after all NI packages are removed, uninstall NI Package Manager from Windows Apps / Installed apps. Do not remove NI Package Manager first.
4. Restart before treating locked files as residue. If an installer or running NI process still owns files, ask the user to close it or reboot; do not force-stop unrelated processes.

## Residual folders and registry

After the package uninstall and an explicit user confirmation, inspect and delete only these paths when they exist:

```text
C:\Program Files\National Instruments
C:\Program Files (x86)\National Instruments
C:\ProgramData\National Instruments
C:\Users\<username>\AppData\Local\National Instruments
C:\Users\<username>\AppData\Roaming\National Instruments
```

Back up the affected registry keys or tell the user how to do so before deletion. With explicit confirmation, remove only these keys when present:

```text
HKEY_LOCAL_MACHINE\SOFTWARE\National Instruments
HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\National Instruments
HKEY_CURRENT_USER\Software\National Instruments
HKEY_CURRENT_USER\Software\WOW6432Node\National Instruments
```

System folders and `HKLM` normally require an elevated administrator process. If permission is denied, explain that elevation is required; do not broaden the deletion scope. If the user confirms ownership/ACL changes for an NI directory, change access only as needed to delete that exact directory, then verify the listed targets are absent.

## Verify and prepare cDAQ reinstallation

1. Verify the five folder paths and four registry keys are absent; report any locked or permission-protected residue precisely.
2. Restart Windows once more.
3. For a minimal cDAQ workflow, reinstall NI Package Manager, then NI-DAQmx. NI-DAQmx supplies the required MAX and System Configuration components. Add FlexLogger only if logging is needed, selecting the appropriate Lite edition when applicable.
4. Do not add NI-VISA solely for cDAQ. Install it later only if the user needs instrument control through VISA (for example, an oscilloscope or programmable supply).
5. Before choosing versions, check the current compatibility and release notes for the user's cDAQ chassis/modules and Windows version.

## Official references

- NI Clean Uninstall: <https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU000000DhqL0AS>
- MAX configuration reset: <https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8awSAC>
