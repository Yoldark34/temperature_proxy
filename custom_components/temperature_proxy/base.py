"""Base entity that tracks whatever sensor the proxy's select currently points to."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, State, callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event

from .const import UNIQUE_ID_SELECT
from .helpers import async_get_entity_id, device_info


class SourceTrackingEntity(Entity):
    """Entity that mirrors the sensor currently selected by this proxy's select entity."""

    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_device_info = device_info(entry)
        self._select_entity_id: str | None = None
        self._source_entity_id: str | None = None
        self._unsub_select = None
        self._unsub_source = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._select_entity_id = async_get_entity_id(
            self.hass, "select", self._entry.entry_id, UNIQUE_ID_SELECT
        )
        if self._select_entity_id is None:
            return

        self._unsub_select = async_track_state_change_event(
            self.hass, [self._select_entity_id], self._handle_select_changed
        )
        self.async_on_remove(self._unsub_select)
        self._track_source(self.hass.states.get(self._select_entity_id))

    @callback
    def _handle_select_changed(self, event: Event[EventStateChangedData]) -> None:
        self._track_source(event.data["new_state"])

    @callback
    def _track_source(self, select_state: State | None) -> None:
        if self._unsub_source is not None:
            self._unsub_source()
            self._unsub_source = None

        new_source_entity_id = None
        if select_state is not None and select_state.state not in (
            None,
            "unknown",
            "unavailable",
            "",
        ):
            new_source_entity_id = select_state.state

        self._source_entity_id = new_source_entity_id

        if self._source_entity_id is not None:
            self._unsub_source = async_track_state_change_event(
                self.hass, [self._source_entity_id], self._handle_source_changed
            )
            self.async_on_remove(self._unsub_source)

        source_state = (
            self.hass.states.get(self._source_entity_id)
            if self._source_entity_id
            else None
        )
        self._async_source_updated(source_state)
        if self.hass is not None:
            self.async_write_ha_state()

    @callback
    def _handle_source_changed(self, event: Event[EventStateChangedData]) -> None:
        self._async_source_updated(event.data["new_state"])
        self.async_write_ha_state()

    def _async_source_updated(self, source_state: State | None) -> None:
        """Subclasses override this to update their own state from the source."""
        raise NotImplementedError
