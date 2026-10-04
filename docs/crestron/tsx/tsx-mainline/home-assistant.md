# Home Assistant

The panel shows one Home Assistant dashboard. It also appears in Home Assistant as one device. The examples use the server `https://ha.example.org` and the device name `my-panel`.

## Add the panel

The panel uses the ESPHome native API. It needs no broker. Home Assistant finds it with zeroconf on port 6053.

1. Connect the panel to the same network as Home Assistant.
2. Open `https://ha.example.org` in a browser.
3. Open **Settings**, then **Devices & services**.
4. Find the discovered ESPHome device and select **Add**.
5. Enter the encryption key if the panel has one.
6. Assign the device to an area.

The panel has no keyboard. To log the kiosk in, or to create the panel tokens with the provisioning scripts, see the [Home Assistant integration](tsx-xx60-linux/ha.md) page.

!!! note
    MQTT is a fallback transport. The default is the ESPHome API.

## Main entities

The panel announces an entity only if it has the hardware. Replace `<panel>` with the name of your panel.

| Entity | Type | Use |
|---|---|---|
| `light.<panel>_led_bar` | Light | The LED bar, with effects |
| `light.<panel>_key_leds` | Light | The brightness of the key LEDs |
| `switch.<panel>_screen` | Switch | Screen on or off |
| `number.<panel>_backlight` | Number | A fixed backlight level |
| `number.<panel>_blank_timeout` | Number | Seconds without input before the screen goes dark. 0 means never |
| `binary_sensor.<panel>_touched_recently` | Binary sensor | On for 30 seconds after a touch or key press |
| `event.<panel>_key_<name>` | Event | One for each front key, for example `event.<panel>_key_power` |
| `update.<panel>_update` | Update | The status of `tsx-autoupdate` |

The device also has a kiosk URL text, an orientation select, a reload button, a reboot button and sensors for the CPU temperature, the uptime and the IP address.

## Voice satellite

The panel can be a voice satellite for Home Assistant. The NC models have no microphone and cannot do this.

1. On the setup page of the panel, set `VOICE` to on.
2. In Home Assistant, accept the ESPHome discovery for the panel. If no discovery shows, add the panel with host `<panel-ip>` and port 6053.
3. Go to **Settings → Voice assistants**. Make an Assist pipeline with a speech-to-text engine and a text-to-speech engine.
4. Select this pipeline for the panel satellite.

The panel detects the wake word itself. You can also bind a front key to start a conversation (push-to-talk). With `VOICE` on, the device has these extra entities:

| Entity | Type | Use |
|---|---|---|
| `assist_satellite.<panel>_assist_satellite` | Assist satellite | The voice satellite |
| `select.<panel>_wake_word` | Select | The wake word phrase |
| A media player | Media player | Spoken replies and announcements |

## LED bar light

The LED bar is a USB accessory. The light has color, brightness and effects. The stock bar firmware offers `None` and `Pulse`.

The optional firmware TSX-LEDBAR adds more effects. See [tsx-ledbar-fw](tsx-ledbar-fw/index.md).

| Effect | What it does | Needs |
|---|---|---|
| `Pulse` | A software breathing effect | Any bar |
| `Breathe` | The bar breathes in the light color | TSX-LEDBAR |
| `Blink` | The bar blinks in the light color | TSX-LEDBAR |
| `Rainbow` | The bar cycles through the hues | TSX-LEDBAR |
| `Chase` | A dot runs down both sides in 1.5 seconds | TSX-LEDBAR 0.1.3 or later |
| `Fill` | A level bar grows from the bottom. The brightness sets the height | TSX-LEDBAR 0.1.3 or later |
| `Spectrum` | The hues move down the right side and up the left side. One turn takes 10 seconds | TSX-LEDBAR 0.1.3 or later |

## LED actions

TSX-LEDBAR 0.1.3 or later adds five actions. Home Assistant registers each one as `esphome.<device>_<action>` when the panel connects. In `<device>`, each `-` of the ESPHome name becomes `_`. The device `my-panel` gives `esphome.my_panel_ledbar_set_led`. Color levels run from 0 to 100, not 0 to 255.

The bar has 16 LEDs. The names are `R1` to `R8` on the right side and `L1` to `L8` on the left side, from top to bottom. The numbers 0 to 15 also work.

| Action | What it does |
|---|---|
| `ledbar_set_led` | Sets one LED, a range such as `R1-R4`, a side (`R` or `L`) or all LEDs (`ALL`) to a color |
| `ledbar_set_side` | Sets one side to a color |
| `ledbar_fill` | Shows a level bar (`percent`) that grows from the bottom |
| `ledbar_split` | Shows one color on the right side and one on the left side |
| `ledbar_clear` | Removes the LED pattern. The bar shows the light color again |

This example sets the first four right LEDs to blue:

```yaml
action: esphome.my_panel_ledbar_set_led
data:
  led: R1-R4
  red: 0
  green: 0
  blue: 60
```

A bad field fails the action with a message, and the bar does not change. Without the firmware, the device lists no actions. The [Home Assistant integration](tsx-xx60-linux/ha.md) page has the fields of each action and the rules for how the actions work with the light and the effects.
