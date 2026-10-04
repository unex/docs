# Supported models

tsx-mainline runs on the Crestron touch panels that use the Amlogic Meson8m2 board `yushan_one`. The NC variants are fully supported. They lack some hardware.

## Models

| Model | Screen | Resolution | Microphone | Camera | Bluetooth |
|---|---|---|---|---|---|
| TSW-760 | 7 inch | 1024 x 600 | Yes | Yes (not tested) | Yes |
| TSW-1060 | 10 inch | 1280 x 800 | Yes | Yes | Yes |
| TSS-10 | 10 inch | 1280 x 800 | Yes | Yes | Yes |
| TSW-760-NC and the other NC variants | Same as the base model | Same as the base model | No | No | No |
| TSW-560 | 5 inch | Not supported | | | |

The TSS-10 has the same hardware as the TSW-1060. It reports its model as TSS-10.

The TSW-560 is not supported. Its display uses MIPI-DSI, not LVDS.

## Hardware on every supported model

| Part | Detail |
|---|---|
| SoC | Amlogic Meson8m2, quad Cortex-A9, Mali-450 GPU |
| Memory | 2 GB RAM |
| Storage | 4 GB eMMC and a removable SD-class card |
| Display | LVDS panel with an LED backlight |
| Touch | FocalTech controller (`edt-ft5x06`) |
| Front keys | 5 capacitive keys on the glass, each with a key LED |
| Ambient light | MAX44009 sensor |
| Audio | ZL38051 voice processor, two TFA9890 amplifiers, two speakers |
| Network | Ethernet with an SMSC LAN8710 PHY |
| USB | One USB-A socket. The optional LED bar plugs into it |
| Power supply | PoE |

The microphone parts are two digital microphones. The Bluetooth part is a CSR8811 chip. The camera is an OV5640 sensor.

## What works

- The kiosk, from the eMMC or from an SD card
- The touchscreen and the front keys with their LEDs
- Screen sleep and wake
- The speakers, the microphones and the voice satellite (not on NC variants)
- The camera on the TSW-1060 and the TSS-10 (off by default). The TSW-760 has the same camera. It is not tested on hardware.
- The ambient light sensor with automatic brightness
- Ethernet
- The Bluetooth proxy for Home Assistant (off by default)
- The network install and the factory restore

## Known limits

- The TSW-760 camera is not tested on hardware. A USB UVC camera in the USB-A socket works on every model.
- The CPU runs at most at 1608 MHz. 1800 MHz is not stable.
- NC variants have no voice satellite and no Bluetooth proxy, because they lack the hardware.

!!! note
    The LED bar firmware is optional. The stock bar firmware is the default. See [tsx-ledbar-fw](tsx-ledbar-fw/index.md).
