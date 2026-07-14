"""The Temperature Proxy integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import PLATFORMS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Temperature Proxy from a config entry.

    The select entity is set up first and awaited on its own: the sensor
    entities look it up by unique_id as soon as they're added, and
    async_forward_entry_setups sets platforms up concurrently, so without
    this ordering they can race and find it missing.
    """
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SELECT])
    await hass.config_entries.async_forward_entry_setups(
        entry, [p for p in PLATFORMS if p != Platform.SELECT]
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
