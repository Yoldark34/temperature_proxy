"""Tests for setting up and unloading a Temperature Proxy config entry."""
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from custom_components.temperature_proxy.const import DOMAIN

from .common import setup_proxy_entry


async def test_setup_creates_one_device_with_four_entities(hass: HomeAssistant) -> None:
    """Setting up an entry creates a single device holding all 4 entities."""
    entry = await setup_proxy_entry(hass, "Fridge Proxy")

    dev_reg = dr.async_get(hass)
    device = dev_reg.async_get_device(identifiers={(DOMAIN, entry.entry_id)})
    assert device is not None
    assert device.name == "Fridge Proxy"

    ent_reg = er.async_get(hass)
    entities = er.async_entries_for_config_entry(ent_reg, entry.entry_id)
    unique_id_suffixes = {e.unique_id.removeprefix(f"{entry.entry_id}_") for e in entities}

    assert unique_id_suffixes == {
        "source_select",
        "value",
        "source_name",
        "source_storage",
    }
    assert {e.entity_id.split(".")[0] for e in entities} == {"select", "sensor", "text"}
    assert all(e.device_id == device.id for e in entities)


async def test_unload_entry(hass: HomeAssistant) -> None:
    """Unloading a config entry cleanly removes its platforms."""
    entry = await setup_proxy_entry(hass)

    assert entry.state is ConfigEntryState.LOADED
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
