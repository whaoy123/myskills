---
name: national-instruments-cdaq-setup
description: Install a clean, minimal Windows cDAQ acquisition environment with NI Package Manager, NI-DAQmx/MAX, and FlexLogger Lite. Use after a clean uninstall or for a new cDAQ measurement PC; do not use for a targeted driver repair.
---

# NI cDAQ Setup

Set up the smallest practical NI software stack for cDAQ acquisition:

```text
NI Package Manager → NI-DAQmx + MAX → FlexLogger Lite
```

Do not install NI-VISA merely because it is available. It is needed for controlling external instruments, not normal cDAQ acquisition. Keep existing TDMS/CSV data and FlexLogger projects outside the software-install scope.

## Before installing

1. Confirm the PC is supported by the selected NI releases and identify the cDAQ chassis/modules when compatibility is uncertain. Prefer a current NI-DAQmx release for a clean Windows 11 system; use a hardware-compatible release instead if an older chassis or module requires one.
2. Check that the prior clean-uninstall process has completed and Windows has restarted. If MAX/DAQmx was just installed, complete its required reboot before installing FlexLogger.
3. Confirm adequate free storage. NI-DAQmx can require several GB and FlexLogger may download a large dependency set.

## Install sequence

### 1. NI Package Manager

Download and install the current Windows NI Package Manager from NI's official download page. NI may require account sign-in to download. Launch it as administrator when using the GUI.

### 2. NI-DAQmx and MAX

Install NI-DAQmx, then ensure **NI Measurement & Automation Explorer (MAX)** is selected or installed alongside it. Do not assume MAX is always a hard dependency of the top-level DAQmx package.

Keep the DAQmx install minimal: omit optional LabVIEW development support, C/C++ support, and unrelated drivers unless the user's workflow needs them. Accept the driver components needed for the target hardware. Let the installer defer reboot requests until its current transaction is complete, then restart Windows.

If controlled command-line installation is appropriate, use the official NI Package Manager feed for the selected release and install the two explicit packages:

```text
ni-daqmx
ni-max
```

Adding system feeds and installing software requires an elevated process. Stop if UAC is declined or if the requested driver is incompatible; do not bypass compatibility checks.

### 3. FlexLogger Lite

Install the current hardware-compatible FlexLogger package after the reboot. FlexLogger Lite and Professional use the same application package; without a Professional license, use the Lite edition.

FlexLogger can require components such as NI LabVIEW Runtime, NI-Sync, NI-XNET, .NET runtime, and DIAdem/TDMS support. These are application dependencies, not a reason to add unrelated NI products. Do not add NI-VISA unless the user separately asks to control an external VISA instrument.

Allow the package transaction to finish before launching FlexLogger or restarting. Large downloads and many small MSI installations are normal; monitor installer status and Windows Installer events when UI progress is unavailable. Escalate only for actual installer errors, blocked UAC, insufficient storage, or an explicit licensing problem.

## Verify handoff

After the final reboot, verify:

1. NI MAX opens and lists the connected cDAQ chassis/modules under **Devices and Interfaces**.
2. The chassis self-test or module test panels work when supported.
3. FlexLogger starts and allows a new Lite project to be created.
4. A basic channel configuration discovers the DAQmx device and can preview a measurement.

Do not create DAQmx tasks, edit cDAQ network configuration, update chassis firmware, or start a measurement unless the user asks. Report the installed NI-DAQmx, MAX, and FlexLogger versions plus any optional dependencies installed automatically.

## Official references

- NI Package Manager: <https://www.ni.com/en/support/downloads/software-products/download.package-manager.html>
- NI-DAQmx download: <https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html>
- FlexLogger download: <https://www.ni.com/en/support/downloads/software-products/download.flexlogger.html>
- FlexLogger resources and installation: <https://www.ni.com/en/shop/data-acquisition-and-control/flexlogger/resources.html>
