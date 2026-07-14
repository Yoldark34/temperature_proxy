"""Tests for the hidden Source Storage text entity."""
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_registry import RegistryEntryHider

from custom_components.temperature_proxy.const import UNIQUE_ID_SELECT, UNIQUE_ID_TEXT
from custom_components.temperature_proxy.helpers import async_get_entity_id

from .common import MockTemperatureSensor, register_mock_entity, select_source, setup_proxy_entry


async def test_storage_is_diagnostic_and_hidden_by_default(hass: HomeAssistant) -> None:
    """The storage entity is tucked away as a diagnostic, hidden entity."""
    entry = await setup_proxy_entry(hass)
    text_entity_id = async_get_entity_id(hass, "text", entry.entry_id, UNIQUE_ID_TEXT)

    ent_reg = er.async_get(hass)
    registry_entry = ent_reg.async_get(text_entity_id)

    assert registry_entry.entity_category is EntityCategory.DIAGNOSTIC
    assert registry_entry.hidden_by is RegistryEntryHider.INTEGRATION


async def test_storage_mirrors_selection(hass: HomeAssistant) -> None:
    """The storage entity's value tracks whatever the select currently points to."""
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "kitchen", "Kitchen"), "sensor"
    )
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    text_entity_id = async_get_entity_id(hass, "text", entry.entry_id, UNIQUE_ID_TEXT)

    assert hass.states.get(text_entity_id).state == ""

    await select_source(hass, select_entity_id, "sensor.kitchen")

    assert hass.states.get(text_entity_id).state == "sensor.kitchen"


async def test_setting_valid_text_value_drives_the_select(hass: HomeAssistant) -> None:
    """Writing a valid sensor entity_id to the storage entity updates the selector too."""
    await register_mock_entity(
        hass, MockTemperatureSensor(hass, "kitchen", "Kitchen"), "sensor"
    )
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    text_entity_id = async_get_entity_id(hass, "text", entry.entry_id, UNIQUE_ID_TEXT)

    await hass.services.async_call(
        "text",
        "set_value",
        {"entity_id": text_entity_id, "value": "sensor.kitchen"},
        blocking=True,
    )

    assert hass.states.get(select_entity_id).state == "sensor.kitchen"


async def test_setting_invalid_text_value_is_ignored(hass: HomeAssistant) -> None:
    """Writing something that isn't a valid option leaves the select untouched."""
    entry = await setup_proxy_entry(hass)
    select_entity_id = async_get_entity_id(hass, "select", entry.entry_id, UNIQUE_ID_SELECT)
    text_entity_id = async_get_entity_id(hass, "text", entry.entry_id, UNIQUE_ID_TEXT)

    await hass.services.async_call(
        "text",
        "set_value",
        {"entity_id": text_entity_id, "value": "sensor.does_not_exist"},
        blocking=True,
    )

    assert hass.states.get(select_entity_id).state == "unknown"
