"""Shared helpers for the Temperature Proxy integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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
