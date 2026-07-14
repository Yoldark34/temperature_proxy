# Temperature Proxy

A Home Assistant integration that creates a "pointer" device: pick any
`sensor.*` entity with `device_class: temperature` from a dropdown, and the
proxy mirrors its value under a stable entity_id that never changes even if
you swap the underlying sensor.

## Install via HACS

1. HACS → Integrations → ⋮ → Custom repositories → add this repo's URL, category "Integration".
2. Install "Temperature Proxy", restart Home Assistant.
3. Settings → Devices & Services → Add Integration → search **Temperature Proxy**.
4. Name the device (you can add as many proxies as you like).

## What you get per device

- **Source Sensor** (`select.*`) — pick which temperature sensor to mirror. Options refresh automatically as sensors appear/disappear, and the selection survives restarts.
- **Temperature** (`sensor.*`) — the mirrored numeric value, `device_class: temperature`.
- **Source Name** (`sensor.*`) — the friendly name of whatever is currently selected.
- **Source Storage** (`text.*`, hidden/diagnostic) — a mirror of the current selection, kept for visibility/automations. Not required for restart persistence — the selector restores itself.

No YAML, no helpers, no automations to maintain by hand.

## Manual install

Copy `custom_components/temperature_proxy` into your Home Assistant `custom_components` folder and restart.
