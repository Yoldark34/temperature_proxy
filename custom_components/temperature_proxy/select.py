"""Select entity used to pick which temperature sensor a proxy points at."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    async_track_state_added_domain,
    async_track_state_removed_domain,
)
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CONF_SOURCE_SENSOR, UNIQUE_ID_SELECT
from .helpers import device_info, get_temperature_sensor_entities


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([TemperatureProxySourceSelect(entry)])


class TemperatureProxySourceSelect(SelectEntity, RestoreEntity):
    """The 'pointer' that decides which real sensor this proxy mirrors."""

    _attr_has_entity_name = True
    _attr_name = "Source Sensor"
    _attr_icon = "mdi:thermometer-lines"
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{UNIQUE_ID_SELECT}"
        self._attr_device_info = device_info(entry)
        self._attr_options: list[str] = []
        self._attr_current_option: str | None = None
        self._pending_restore: str | None = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in (
            None,
            "unknown",
            "unavailable",
            "",
        ):
            self._pending_restore = last_state.state
        else:
            # No prior restored state means this entity has never existed
            # before (fresh setup, or its registry entry was deleted) -
            # fall back to the sensor chosen in the config flow.
            self._pending_restore = self._entry.data.get(CONF_SOURCE_SENSOR)

        self._refresh_options()
        self._try_restore()

        self.async_on_remove(
            self.hass.bus.async_listen(
                EVENT_HOMEASSISTANT_STARTED, self._handle_ha_started
            )
        )
        self.async_on_remove(
            async_track_state_added_domain(
                self.hass, ["sensor"], self._handle_sensor_topology_changed
            )
        )
        self.async_on_remove(
            async_track_state_removed_domain(
                self.hass, ["sensor"], self._handle_sensor_topology_changed
            )
        )

    @callback
    def _handle_ha_started(self, event: Event) -> None:
        self._refresh_options()
        self._try_restore()
        self.async_write_ha_state()

    @callback
    def _handle_sensor_topology_changed(
        self, event: Event[EventStateChangedData]
    ) -> None:
        self._refresh_options()
        self._try_restore()
        self.async_write_ha_state()

    def _refresh_options(self) -> None:
        self._attr_options = get_temperature_sensor_entities(
            self.hass, self._entry.entry_id
        )
        if (
            self._attr_current_option is not None
            and self._attr_current_option not in self._attr_options
        ):
            self._attr_current_option = None

    def _try_restore(self) -> None:
        if (
            self._pending_restore is not None
            and self._attr_current_option is None
            and self._pending_restore in self._attr_options
        ):
            self._attr_current_option = self._pending_restore

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option
        self._pending_restore = option
        self.async_write_ha_state()
