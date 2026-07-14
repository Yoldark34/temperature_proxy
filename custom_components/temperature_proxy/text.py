"""Hidden diagnostic entity mirroring the selected sensor's entity_id.

This entity is not required for restoring the selection across restarts
(the select entity restores itself), it exists purely as a visible/hidden
record of the current selection, and as a convenience: setting its value
to a valid temperature sensor entity_id will drive the select entity too.
"""
from __future__ import annotations

from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, EntityCategory
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import SourceTrackingEntity
from .const import UNIQUE_ID_SELECT, UNIQUE_ID_TEXT
from .helpers import async_get_entity_id


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([TemperatureProxyStorageText(entry)])


class TemperatureProxyStorageText(SourceTrackingEntity, TextEntity):
    """Diagnostic mirror of the select entity's current option, hidden by default."""

    _attr_has_entity_name = True
    _attr_name = "Source Storage"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_visible_default = False
    _attr_native_min = 0
    _attr_native_max = 255

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_{UNIQUE_ID_TEXT}"
        self._attr_native_value = ""

    def _async_source_updated(self, source_state: State | None) -> None:
        self._attr_native_value = self._source_entity_id or ""

    async def async_set_value(self, value: str) -> None:
        select_entity_id = async_get_entity_id(
            self.hass, "select", self._entry.entry_id, UNIQUE_ID_SELECT
        )
        if select_entity_id is None:
            return

        select_state = self.hass.states.get(select_entity_id)
        if select_state is None or value not in select_state.attributes.get(
            "options", []
        ):
            return

        await self.hass.services.async_call(
            SELECT_DOMAIN,
            "select_option",
            {ATTR_ENTITY_ID: select_entity_id, "option": value},
            blocking=True,
        )
