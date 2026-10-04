# Install a panel

This page shows the short path to install tsx-mainline on a TSW-760, TSW-1060 or TSS-10 panel. The steps are the same for the NC variants. The [install and reinstall page](tsx-xx60-linux/install.md) has every option and the troubleshooting table.

## Before you start

- Read [Getting started](getting-started.md).
- Use a Linux computer that reaches the panel in both directions. The panel connects back to the computer on TCP ports 8079 and 8081, so a one-way VPN or NAT does not work.
- Make sure the computer has `sshpass`, `ssh`, `python3`, `curl`, `sha256sum`, `ip`, `git` and `zstd`.

!!! note
    The installer needs a root shell on the panel over the Crestron SSH service. See "Root over the Crestron sshd" in the [install and reinstall page](tsx-xx60-linux/install.md).

## Steps

1. Power the panel over PoE and connect it to the network.
2. Find the IP address of the panel. This page calls it `<panel-ip>`.
3. Open the releases page of the `tsx-xx60-linux` repository: <https://github.com/tsx-mainline/tsx-xx60-linux/releases>.
4. Download `tsx-xx60-lts-payload.tar.zst` and `SHA256SUMS`. For the stable kernel (7.2), download `tsx-xx60-stable-payload.tar.zst` instead.
5. Clone the repository and check out the tag of the release:

    ```sh
    git clone https://github.com/tsx-mainline/tsx-xx60-linux
    cd tsx-xx60-linux
    git checkout <release-tag>
    ```

6. Move the two downloaded files into this directory.
7. Verify the archive with `sha256sum -c --ignore-missing SHA256SUMS`.
8. Unpack the archive:

    ```sh
    mkdir -p installer/out/payload
    tar --zstd -xf tsx-xx60-lts-payload.tar.zst -C installer/out/payload
    ```

9. Set the variable `TSX_ADMIN_PW` to the Crestron administrator password of the panel.
10. Run the installer. Use `--kernel lts` (kernel 6.18) or `--kernel stable` (kernel 7.2). The option is required, and it must match the archive.

    ```sh
    installer/tsx-install-mainline <panel-ip> \
      --payload installer/out/payload --kernel lts
    ```

11. Answer the prompts: panel name, Home Assistant URL, time zone and so on. Press Enter to keep a default.
12. Enter a root password or an SSH public key when the installer asks. The install stops without one.
13. Type `INSTALL` at each confirmation.
14. Wait for the panel to restart. The installer prints its progress.
15. Look at the panel screen. The kiosk shows your dashboard. It shows the setup page if you gave no URL.

## If a step fails

1. Run the same command again. The install resumes.
2. If the panel does not answer, power cycle it once. The panel then boots the previous system.
3. If the panel still fails, read [Recovery](tsx-xx60-linux/recovery.md).

The install and reinstall page lists each symptom with its cause and fix.

## After the install

Connect the panel to Home Assistant. See [Home Assistant](home-assistant.md). To install a new release on a panel that already runs tsx-mainline, run the same command again. See "Reinstall or update a panel that runs mainline" in the install and reinstall page.
