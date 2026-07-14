# Temperature Proxy

A Home Assistant integration that creates a "pointer" device: pick any
`sensor.*` entity with `device_class: temperature` from a dropdown, and the
proxy mirrors its value under a stable entity_id that never changes even if
you swap the underlying sensor.

## Installation

### Method 1: HACS

One-click installation from HACS:

[![Open your Home Assistant instance and open the Temperature Proxy integration inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Yoldark34&repository=temperature_proxy&category=integration)

Or, HACS → Integrations → ⋮ → Custom repositories → add `https://github.com/Yoldark34/temperature_proxy`, category **Integration** → Install → restart Home Assistant.

### Method 2: Manual install

Copy `custom_components/temperature_proxy` into your Home Assistant `custom_components` folder and restart.

## Configuration

[![Open your Home Assistant instance and start setting up a new Temperature Proxy integration instance.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=temperature_proxy)

Or, Settings → Devices & Services → Add Integration → search **Temperature Proxy** → name the device and pick the temperature sensor it should start out pointing to. You can add as many proxies as you like, and repoint any of them later from its Source Sensor selector.

## What you get per device

- **Source Sensor** (`select.*`) — pick which temperature sensor to mirror. Options refresh automatically as sensors appear/disappear, and the selection survives restarts on its own (via Home Assistant's built-in entity restore).
- **Temperature** (`sensor.*`) — the mirrored numeric value, `device_class: temperature`. Its own display name follows the selected source (its friendly name, or its entity_id without the `sensor.` prefix if it has none), so you can tell what it's mirroring at a glance without a separate entity.

No YAML, no helpers, no automations to maintain by hand.
