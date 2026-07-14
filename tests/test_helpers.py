"""Tests for helpers.resolve_source_display_name."""
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.temperature_proxy.helpers import resolve_source_display_name


async def test_uses_friendly_name_attribute_when_no_registry_entry(hass: HomeAssistant) -> None:
    """A bare entity with no registry entry falls back to its friendly_name attribute."""
    state = State("sensor.bare", "20.0", {"friendly_name": "Bare Sensor"})
    assert resolve_source_display_name(hass, "sensor.bare", state) == "Bare Sensor"


async def test_falls_back_to_entity_id_when_nothing_available(hass: HomeAssistant) -> None:
    """With no registry entry and no friendly_name attribute, use the bare entity_id."""
    state = State("sensor.bare", "20.0", {})
    assert resolve_source_display_name(hass, "sensor.bare", state) == "bare"


async def test_falls_back_to_entity_id_when_state_is_none(hass: HomeAssistant) -> None:
    """With no state at all, still fall back to the bare entity_id."""
    assert resolve_source_display_name(hass, "sensor.bare", None) == "bare"


async def _create_device_backed_entity(
    hass: HomeAssistant,
    *,
    device_name: str,
    device_name_by_user: str | None = None,
    entity_name: str | None = None,
    original_name: str = "Temperature",
) -> str:
    """Register a device + has_entity_name entity, mimicking Zigbee2MQTT discovery."""
    fake_entry = MockConfigEntry(domain="fake_zigbee")
    fake_entry.add_to_hass(hass)

    dev_reg = dr.async_get(hass)
    device = dev_reg.async_get_or_create(
        config_entry_id=fake_entry.entry_id,
        identifiers={("fake_zigbee", "device-1")},
        name=device_name,
    )
    if device_name_by_user is not None:
        dev_reg.async_update_device(device.id, name_by_user=device_name_by_user)

    ent_reg = er.async_get(hass)
    entry = ent_reg.async_get_or_create(
        "sensor",
        "fake_zigbee",
        "unique-1",
        device_id=device.id,
        original_name=original_name,
        has_entity_name=True,
    )
    if entity_name is not None:
        ent_reg.async_update_entity(entry.entity_id, name=entity_name)

    return entry.entity_id


async def test_uses_device_name_when_entity_not_personalized(hass: HomeAssistant) -> None:
    """A has_entity_name entity the user hasn't renamed uses its device's name.

    This mirrors the Zigbee2MQTT case: the entity's own default name is just
    the generic "Temperature", and the composed friendly_name would be a
    redundant "Temp Chambre Temperature" - the device name alone is the
    useful label.
    """
    entity_id = await _create_device_backed_entity(hass, device_name="Temp Chambre")
    state = State(entity_id, "20.0", {"friendly_name": "Temp Chambre Temperature"})

    assert resolve_source_display_name(hass, entity_id, state) == "Temp Chambre"


async def test_prefers_device_name_by_user_over_auto_device_name(hass: HomeAssistant) -> None:
    """A user-set device name (even set outside HA, e.g. via Z2M) wins over the raw device name."""
    entity_id = await _create_device_backed_entity(
        hass, device_name="0x00158d0001", device_name_by_user="Temp Chambre"
    )
    state = State(entity_id, "20.0", {"friendly_name": "0x00158d0001 Temperature"})

    assert resolve_source_display_name(hass, entity_id, state) == "Temp Chambre"


async def test_prefers_personalized_entity_name_over_device_name(hass: HomeAssistant) -> None:
    """If the user renamed the entity itself, that takes priority over the device name."""
    entity_id = await _create_device_backed_entity(
        hass, device_name="Temp Chambre", entity_name="Bedroom Probe"
    )
    state = State(entity_id, "20.0", {"friendly_name": "Temp Chambre Temperature"})

    assert resolve_source_display_name(hass, entity_id, state) == "Bedroom Probe"
