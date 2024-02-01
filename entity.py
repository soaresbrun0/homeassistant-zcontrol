"""Base entity for ZControl® integration."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .coordinator import ZControlDataUpdateCoordinator


class ZControlEntity(CoordinatorEntity[ZControlDataUpdateCoordinator]):
    """Define a ZControl® entity."""

    @dataclass
    class __CoordinatorContext:
        value_keypath: [Any]
        value_modifier: Callable | None

    def __init__(
        self,
        coordinator: ZControlDataUpdateCoordinator,
        name: str,
        value_keypath: [Any],
        value_modifier: Callable | None = None,
        device_class: str | None = None,
        unit_of_measurement: str | None = None,
    ) -> None:
        """Initialize a ZControl® entity."""
        context = self.__CoordinatorContext(value_keypath, value_modifier)
        super().__init__(coordinator, context)

        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = slugify(f"{coordinator.device.device_id} {name}")
        self._attr_name = name
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_available = False

        # placeholder will get replaced with the actual domain later on
        self.entity_id = f"placeholder.{self._attr_unique_id}"

    @property
    def __value_from_coordinator(self) -> Any:
        context: self.__CoordinatorContext = self.coordinator_context
        value = self.coordinator.device

        for key in context.value_keypath:
            if value is None:
                break
            if isinstance(key, str) and hasattr(value, key): # property
                value = getattr(value, key)
            elif hasattr(value, "__getitem__"): # subscript (e.g. list, dict)
                value = value[key]
            else:
                raise AttributeError(f'{type(value)} missing required attribute "{key}".')

        if context.value_modifier is not None:
            value = context.value_modifier(value)

        return value

    @callback
    def _handle_coordinator_update(self) -> None:
        super()._handle_coordinator_update()
        value = self.__value_from_coordinator
        self._update_value(value)
        self._attr_available = value is not None
        self._attr_device_info = self.coordinator.device_info
        self.async_write_ha_state()

    def _update_value(self, value: Any) -> None:
        raise NotImplementedError

