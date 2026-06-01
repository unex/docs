# UniFi Switch Recovery

Tested on: **US-48-750W**

## Symptoms

The switch is unreachable on the network and its LEDs indicate a boot loop (repeatedly cycling through startup patterns). On the serial console you will see the switch restarting over and over. Each cycle ends with:

```text
...running /sbin/init
init started: BusyBox v1.23.2 (2021-11-17 07:22:05 UTC)
can't run '/etc/rc.d/rc.platform': No such file or directory
Please press Enter to activate this console. umount: can't remount rootfs read-only
Sent SIGKILL to all processes
Requesting system reboot
[  52.860000] Disabling non-boot CPUs ...
[  52.860000] Restarting system.
```

## Background

These switches have two firmware partitions (kernel0 and kernel1) managed by a proprietary UBNT boot selector. If the active partition is corrupt or the UBNT app fails to initialize, the device may boot loop or get stuck. You can bypass the UBNT boot selector from U-Boot to manually boot a known-good partition, then let the UniFi controller reflash clean firmware.

## Flash Layout (32MB device)

| Partition   | MTD   | Offset       | Size    |
|-------------|-------|--------------|---------|
| u-boot      | mtd0  | 0x00000000   | 768 KB  |
| u-boot-env  | mtd1  | 0x000c0000   | 64 KB   |
| shmoo       | mtd2  | 0x000d0000   | 64 KB   |
| kernel0     | mtd3  | 0x000e0000   | 15 MB   |
| kernel1     | mtd4  | 0x000fe0000  | ~15 MB  |
| cfg         | mtd5  | 0x001ef0000  | 1 MB    |
| EEPROM      | mtd6  | 0x001ff0000  | 64 KB   |

## Hardware Required

- Serial console cable (3.3V TTL UART)
- Console settings: **115200 8N1**, no flow control

## Recovery Procedure

### 1. Connect serial console

Connect to the switch's UART header and open a terminal at 115200 baud before powering on.  Some switches have a console port on the rear, which can be used with a Cisco style console cable.

### 2. Interrupt autoboot

Power on the switch. Watch for:

```text
Hit any key to stop autoboot:  0
```

Press any key before the countdown reaches 0. You will get a `u-boot>` prompt.

### 3. Identify the broken kernel

Before interrupting autoboot, watch the serial output. The UBNT app prints which partition it is attempting to boot:

```text
ubnt_bootsel_init: bootsel magic=a34de82b, bootsel = 1
Boot partition selected = 1
Verifying 'kernel1' partition: OK
```

`bootsel = 0` → kernel0, `bootsel = 1` → kernel1. The one selected here is the broken one causing the boot loop. If this output is absent entirely, the UBNT app itself failed to initialize - start with kernel0 in that case.

On the next boot cycle, press any key at `Hit any key to stop autoboot` to get the u-boot prompt.

### 4. Boot the working kernel

Boot the partition that was **not** selected by the UBNT app.

**kernel0** (offset `0x0E0000`, size `0xF00000`):

```sh
sf probe
sf read 0x01000000 0x000e0000 0x00f00000
bootm 0x01000000
```

**kernel1** (offset `0xFE0000`, size `0xF10000`):

```sh
sf probe
sf read 0x01000000 0x00fe0000 0x00f10000
bootm 0x01000000
```

Continue once the switch has booted and you have a console prompt.

### 4. Upgrade firmware via controller

Once the switch is adopted by the UniFi controller, trigger a firmware upgrade from the controller UI. The controller flashes new firmware to kernel0 and reboots the device.

### 5. Verify normal boot

After reboot, the UBNT boot selector should initialize normally and select kernel0:

```text
ubnt_bootsel_init: bootsel magic=a34de82b, bootsel = 0
Boot partition selected = 0
Verifying 'kernel0' partition: OK
```

The switch will connect to the controller and be fully managed.

## References

- https://community.ui.com/questions/US-24-POE-on-a-boot-loop-any-tricks/a3f58ffd-9af2-4f18-a260-7d9e9566f689?page=0&reply=2
- https://community.ui.com/questions/US-48-750W-boot-loop-corrupt-file-system/6c98b6dc-afab-4cb5-b9f0-b495e2f10456
- https://community.ui.com/questions/Semi-Dead-48-500-switch/46b80099-4960-46ea-9481-0d91f071628c
- https://community.ui.com/questions/US-24-250W-flashing-white-light/f332b43f-0f88-4f55-9160-3f76547c27d3
- https://community.ui.com/questions/Semi-Dead-48-500-switch/46b80099-4960-46ea-9481-0d91f071628c
