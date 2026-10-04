# Getting started

## What you need

- A supported panel. See [Supported models](models.md).
- A PoE switch port or a PoE injector.
- A network cable and a network that gives the panel an IP address.
- A Linux computer that reaches the panel over the network. It runs the installer.
- The Crestron administrator password of the panel. A new panel has no account. The installer creates it from the password that you give in `TSX_ADMIN_PW`.
- Home Assistant. This is optional. The panel also shows any web page.

A UART serial cable is optional. The installer works over the network alone, except for one case: a factory panel has no root shell over SSH. The one-time patch of the root shell needs a root session, for example over the serial console. See the [install and reinstall page](tsx-xx60-linux/install.md).

## Risks

!!! danger
    An install replaces the factory software. This voids the manufacturer warranty.

- An interrupted or incorrect flash can leave a panel unable to boot.
- The tools never write U-Boot or the first 1 MiB of the storage. No software can repair that region.
- After a failed step, the panel falls back to stock Android or to the rescue system.
- You use the tools at your own risk. Back up anything on the panel that you cannot replace.

## Return to stock firmware

The installer keeps either part of Android or a small rescue system. You can always return the panel to stock.

1. In the `tsx-xx60-linux` repository, run `rootfs/vendor-fetch.sh`. It downloads the public Crestron firmware package (a `.puf` file) and checks it. The project does not ship the file. You can also give your own copy with `--puf FILE`.
2. Make sure the Linux computer reaches the panel.
3. Run `installer/tsx-restore-factory <panel-ip>`.
4. Wait for the command to finish. Do not power off the panel.

The restore needs no backup. It erases the tsx-mainline install and the data of the panel, and it keeps the identity of the panel. See [Recovery](tsx-xx60-linux/recovery.md).

## Next step

Follow [Install a panel](install.md).
