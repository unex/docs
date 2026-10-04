# tsx-mainline

tsx-mainline is mainline Linux for Crestron touch panels. It replaces the vendor Android firmware. The panel shows a Home Assistant dashboard full screen. It also works as a media player and a Bluetooth proxy for Home Assistant.

tsx-mainline supports the TSW-760, TSW-1060 and TSS-10. See [Supported models](models.md).

!!! warning
    An install replaces the factory software and voids the manufacturer warranty. Read [Getting started](getting-started.md) first.

## Where to start

1. Check your panel in [Supported models](models.md).
2. Read [Getting started](getting-started.md).
3. Follow [Install a panel](install.md).
4. Connect the panel with [Home Assistant](home-assistant.md).
5. Keep the panel current with [Updates and rollback](updates.md).

The [FAQ](faq.md) answers common problems. For a failed install or a panel that does not boot, read [Recovery](tsx-xx60-linux/recovery.md). The [Hardware](../hardware/xx60.md) page lists the panel parts and their support status. To look up the boot flow, the kernel or the root file system, use the sections below.

## Repositories

Each repository has its own section on this site. The pages in a section come from the `docs` folder of the repository.

### tsx-xx60-linux

The mainline kernel, the boot image, the installer and the recovery tools for the TSW-760, TSW-1060 and TSS-10. Start with [tsx-xx60-linux](tsx-xx60-linux/index.md).

### tsx-linux-common

The software that the panels share: base services, rescue screen, boot splash, kiosk, setup page, Home Assistant layer, front buttons and automatic update. Start with [tsx-linux-common](tsx-linux-common/index.md).

### tsx-ledbar-fw

Open firmware for the USB LED bar, with the tools that load it. The stock bar firmware stays the default. Start with [tsx-ledbar-fw](tsx-ledbar-fw/index.md).

### tsx-aports

The signed apk package repository. A panel runs `apk upgrade` to get new kernels and project packages. Start with [tsx-aports](tsx-aports/index.md).

## License

The files of the tsx-mainline project use GPL-2.0-or-later. The kernel uses GPL-2.0, the same as the Linux kernel. Third-party software keeps its own license.

## Trademark

Crestron and the names of Crestron products are trademarks of Crestron Electronics, Inc. This project is independent, community-made software. Crestron Electronics, Inc. does not support or endorse it and is not affiliated with it.
