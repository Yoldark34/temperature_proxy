"""Shared helpers for the Temperature Proxy integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo

from .const import DEVICE_CLASS_TEMPERATURE, DOMAIN


def device_info(entry: ConfigEntry) -> DeviceInfo:
    """Build the DeviceInfo shared by every entity of a config entry."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer="Temperature Proxy",
        model="Temperature Proxy",
        entry_type=DeviceEntryType.SERVICE,
    )


def get_temperature_sensor_entities(hass: HomeAssistant, entry_id: str) -> list[str]:
    """Return every sensor.* entity_id with device_class temperature.

    Entities that belong to this same config entry (i.e. our own proxy
    sensors) are excluded so a proxy can never point at itself.
    """
    ent_reg = er.async_get(hass)
    own_entity_ids = {
        entry.entity_id
        for entry in er.async_entries_for_config_entry(ent_reg, entry_id)
    }

    result = [
        state.entity_id
        for state in hass.states.async_all("sensor")
        if state.attributes.get("device_class") == DEVICE_CLASS_TEMPERATURE
        and state.entity_id not in own_entity_ids
    ]
    return sorted(result)


def async_get_entity_id(
    hass: HomeAssistant, platform: str, entry_id: str, unique_id_suffix: str
) -> str | None:
    """Resolve the current entity_id for one of our own entities by its unique_id."""
    ent_reg = er.async_get(hass)
    return ent_reg.async_get_entity_id(
        platform, DOMAIN, f"{entry_id}_{unique_id_suffix}"
    )


def resolve_source_display_name(
    hass: HomeAssistant, source_entity_id: str, source_state: State | None
) -> str:
    """Best-effort human label for whatever sensor is currently selected.

    Prefers a name the user personalized directly on the source entity
    itself. If they haven't renamed the entity, prefers its device's name
    instead - even if that name wasn't typed by the user in Home Assistant
    (e.g. it came from Zigbee2MQTT discovery) - over the entity's own
    default name. That's because with has_entity_name-style naming the
    entity's own default is usually just a generic word like "Temperature",
    and the device name (e.g. "Temp Chambre") is what actually identifies
    which sensor it is; the state's computed friendly_name would otherwise
    be a redundant "Temp Chambre Temperature".

    Falls back to the computed friendly_name state attribute, then to the
    bare entity_id, for entities with no registry/device data at all.
    """
    entity_entry = er.async_get(hass).async_get(source_entity_id)

    if entity_entry is not None:
        if entity_entry.name is not None:
            return entity_entry.name
        if entity_entry.device_id is not None:
            device = dr.async_get(hass).async_get(entity_entry.device_id)
            device_name = device and (device.name_by_user or device.name)
            if device_name:
                return device_name

    if source_state is not None:
        friendly_name = source_state.attributes.get("friendly_name")
        if friendly_name:
            return friendly_name

    return source_entity_id.removeprefix("sensor.")
