# FAQ

## Which panels work?

The TSW-760, the TSW-1060, the TSS-10 and their NC variants. See [Supported models](models.md).

## Can I go back to stock Android?

Yes. Run `installer/tsx-restore-factory <panel-ip>` in the `tsx-xx60-linux` repository. The command needs the Crestron firmware package. `rootfs/vendor-fetch.sh` downloads it. You need no backup. See [Getting started](getting-started.md) and [Recovery](tsx-xx60-linux/recovery.md).

## Do I need a serial cable?

Usually not. The installer and the restore work over the network. A factory panel is the exception. It has no root shell over SSH. The one-time patch of the root shell needs a root session, for example over the serial console. See [Install a panel](install.md).

## The installer says my IP address is blocked. What do I do?

The Crestron SSH service blocks an address for 24 hours after three failed logins. Log in to the Crestron console from another computer. Run `REMBLOCKEDIP <blocked-ip>`.

## The install stopped. What do I do?

1. Run the same install command again. It resumes in the rescue.
2. If the rescue does not answer, power cycle the panel once. The panel then boots the previous system.
3. If the panel still fails, read [Recovery](tsx-xx60-linux/recovery.md).

## The installer asks for a root password or an SSH key. Why?

A public image has no fixed root password. The install stops until you give a password or a key. The panel applies it at the first boot.

## The panel shows a setup page instead of my dashboard. Why?

You gave no kiosk URL. Enter the Home Assistant URL on the setup page. You can also open `http://<panel-ip>:8080/setup` from a laptop and enter the six-digit pairing code from the panel screen.

## How do I open the setup page again?

Run `tsx-config setup` over ssh, or press the Setup button in the quick settings of the panel. The page opens again for about 15 minutes. Your configuration stays.

## The LED bar does not light. Why?

The LED chips in the bar can fail to start at power-up. The `tsx-ledbar` service then restarts the bar controller, up to 3 times. If the chips still do not start, the log `/var/log/tsx-ledbar.log` shows "LED drivers did not start after 3 restarts".

1. Disconnect the LED bar.
2. Wait 5 seconds.
3. Connect the LED bar again.

## The LED actions do not appear in Home Assistant. Why?

The actions need the bar firmware TSX-LEDBAR 0.1.3 or later. With the stock firmware, the device lists no actions. See [Home Assistant](home-assistant.md).

## Does the voice assistant work on an NC variant?

No. The voice satellite needs a microphone. NC variants have no microphone.

## Does the camera work?

Yes, on the TSW-1060, the TSS-10 and the TSW-760. The TSW-760 camera is not tested on hardware. The camera is off by default. Home Assistant gets a camera entity in snapshot or live mode. See [Home Assistant integration](tsx-xx60-linux/ha.md). NC variants have no camera. A USB UVC camera in the USB-A socket also works.

## Why did the panel restart at night?

The panel installs updates from 03:00 to 05:00. A kernel update needs a restart. See [Updates and rollback](updates.md).

## How do I stop the automatic restart?

Set `REBOOT=never` in `/etc/tsx/autoupdate.conf`.

## How do I switch to the stable kernel?

Run `tsx-kernel-flavor stable` on the panel. Then run `reboot`. See [Updates and rollback](updates.md).

## Which license applies?

The files of the tsx-mainline project use GPL-2.0-or-later. See [tsx-mainline](index.md).
