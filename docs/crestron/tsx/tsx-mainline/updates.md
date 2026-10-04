# Updates and rollback

## The apk repository

The panel installs its software from an apk repository with signed Alpine packages. The repository provides the kernel, Chromium and the other project packages. See [tsx-aports](tsx-aports/index.md).

The address is `https://tsx-aports.unexceptional.net`. The panel lists these repositories in `/etc/apk/repositories`:

```text
https://tsx-aports.unexceptional.net/v3.24/common
https://tsx-aports.unexceptional.net/v3.24/xx60
https://dl-cdn.alpinelinux.org/alpine/v3.24/main
https://dl-cdn.alpinelinux.org/alpine/v3.24/community
```

Keep the project repositories first. The panel then gets the patched Chromium, not the Alpine build.

To update by hand, run `apk upgrade` on the panel.

## Automatic updates

The service `tsx-autoupdate` checks for updates every day. It installs them inside a time window.

- The default window is 03:00 to 05:00 local time.
- The panel installs only while the screen is idle.
- The panel restarts only inside the same window. A kernel update needs a restart.
- To stop the restart, set `REBOOT=never` in `/etc/tsx/autoupdate.conf`. The status then shows "reboot pending".
- After a restart, the service checks the kiosk and the dashboard page. It saves the result.

To see the status, run `tsx-autoupdate status`. To install at once, run `tsx-autoupdate now`. The update entity of the panel in Home Assistant shows the same status. Its Install button runs `tsx-autoupdate now`.

## Kernel flavors

Two kernel flavors exist:

| Flavor | Kernel | Use |
|---|---|---|
| `lts` | 6.18 | The default |
| `stable` | 7.2 | The newest stable kernel |

LTS is the default. Both boot images are on the panel. To switch the flavor, do these steps on the panel:

1. Run `tsx-kernel-flavor` to see the selected flavor.
2. Run `tsx-kernel-flavor stable` to select the other flavor.
3. Run `reboot`.

The command saves the current boot image, writes the boot image of the selected flavor and verifies it. It needs no network. For the other method, `tsx-update-boot`, see [Install and reinstall](tsx-xx60-linux/install.md).

## Rescue system and rollback

The rescue system is a small Linux in the golden recovery slot. It never formats a disk and never installs on its own.

The panel starts the rescue after repeated failed boots. A kiosk that keeps failing alternates between the rescue and stock Android.

1. Look at the panel screen. The rescue shows its IP address and the login.
2. Log in over ssh with your key or your root password.
3. Run `tsx-rescue status` to see the counters.
4. Repair the problem.
5. Run `tsx-rescue done && reboot -f` to go back to the kiosk.

If you set no password, the rescue shows a one-time password on the screen.

To go back to the previous kernel, use the rollback command that `tsx-update-boot` prints. It saves the previous boot image in `/data`. To return to stock Android, see [Getting started](getting-started.md) and [Recovery](tsx-xx60-linux/recovery.md).
