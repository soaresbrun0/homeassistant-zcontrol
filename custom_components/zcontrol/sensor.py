"""Sensors for ZControl® integration."""

from collections.abc import Callable
from typing import Any

from pyzctrl.devices.battery import ZControlBatteryDevice
from pyzctrl.devices.float import ZControlFloatDevice
from pyzctrl.devices.pump import ZControlPumpDevice

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ZControlDataUpdateCoordinator
from .entity import ZControlEntity


class ZControlSensorEntity(ZControlEntity, SensorEntity):
    """Represents a ZControl® sensor."""

    def __init__(
            self,
            coordinator: ZControlDataUpdateCoordinator,
            name: str,
            value_keypath: [Any],
            value_modifier: Callable | None = None,
            device_class: str | None = None,
            state_class: str | None = None,
            unit_of_measurement: str | None = None,
        ) -> None:
        """Initialize a ZControl® sensor entity."""
        super().__init__(
            coordinator,
            name,
            value_keypath,
            value_modifier,
            device_class,
            unit_of_measurement
        )
        self._attr_state_class = state_class

    def _update_value(self, value: Any) -> None:
        self._attr_native_value = value


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up ZControl® binary sensors for the given config entry."""
    coordinator: ZControlDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    device = coordinator.device
    sensors = _create_basic_device_sensors(coordinator)
    if isinstance(device, ZControlBatteryDevice):
        sensors.extend(_create_battery_device_sensors(device, coordinator))
    if isinstance(device, ZControlFloatDevice):
        sensors.extend(_create_float_device_sensors(device, coordinator))
    if isinstance(device, ZControlPumpDevice):
        sensors.extend(_create_pump_device_sensors(device, coordinator))
    async_add_entities(sensors)


def _create_basic_device_sensors(
    coordinator: ZControlDataUpdateCoordinator
) -> [ZControlSensorEntity]:
    return [
        ZControlSensorEntity(
            coordinator,
            value_keypath = ["system_uptime"],
            name = "System Uptime",
            device_class = SensorDeviceClass.DURATION,
            state_class = SensorStateClass.TOTAL,
            unit_of_measurement = UnitOfTime.SECONDS,
        ),
    ]

def _create_battery_device_sensors(
    device: ZControlBatteryDevice,
    coordinator: ZControlDataUpdateCoordinator
) -> [ZControlSensorEntity]:
    sensors: [ZControlSensorEntity] = []
    for battery_type in device.batteries:
        sensors.extend(_create_battery_sensors(battery_type, coordinator))
    return sensors

def _create_battery_sensors(
    battery_type: ZControlBatteryDevice.Battery.Type,
    coordinator: ZControlDataUpdateCoordinator,
) -> [ZControlSensorEntity]:
    battery_name = f"{battery_type.value} Battery"

    return [
        ZControlSensorEntity(
            coordinator,
            f"{battery_name} Voltage",
            value_keypath = ["batteries", battery_type, "voltage"],
            device_class = SensorDeviceClass.VOLTAGE,
            state_class = SensorStateClass.MEASUREMENT,
            unit_of_measurement = UnitOfElectricPotential.VOLT,
        ),
        ZControlSensorEntity(
            coordinator,
            f"{battery_name} Current",
            value_keypath = ["batteries", battery_type, "current"],
            device_class = SensorDeviceClass.CURRENT,
            state_class = SensorStateClass.MEASUREMENT,
            unit_of_measurement = UnitOfElectricCurrent.AMPERE,
        ),
    ]

def _create_float_device_sensors(
    device: ZControlFloatDevice,
    coordinator: ZControlDataUpdateCoordinator,
) -> [ZControlSensorEntity]:
    sensors: [ZControlSensorEntity] = []
    for float_type in device.floats:
        sensors.extend(_create_float_sensors(float_type, coordinator))
    return sensors

def _create_float_sensors(
    float_type: ZControlFloatDevice.Float.Type,
    coordinator: ZControlDataUpdateCoordinator,
) -> [ZControlSensorEntity]:
    float_name = f"{float_type.value} Float"

    return [
        ZControlSensorEntity(
            coordinator,
            f"{float_name} Activation Count",
            value_keypath = ["floats", float_type, "activation_count"],
            state_class = SensorStateClass.TOTAL,
        ),
    ]

def _create_pump_device_sensors(
    device: ZControlPumpDevice,
    coordinator: ZControlDataUpdateCoordinator,
) -> [ZControlSensorEntity]:
    sensors: [ZControlSensorEntity] = []
    for pump_type in device.pumps:
        sensors.extend(_create_pump_sensors(pump_type, coordinator))
    return sensors

def _create_pump_sensors(
    pump_type: ZControlPumpDevice.Pump.Type,
    coordinator: ZControlDataUpdateCoordinator,
) -> [ZControlSensorEntity]:
    pump_name = f"{pump_type.value} Pump"

    return [
        ZControlSensorEntity(
            coordinator,
            f"{pump_name} Current",
            value_keypath = ["pumps", pump_type, "current"],
            device_class = SensorDeviceClass.CURRENT,
            state_class = SensorStateClass.MEASUREMENT,
            unit_of_measurement = UnitOfElectricCurrent.AMPERE,
        ),
        ZControlSensorEntity(
            coordinator,
            f"{pump_name} Runtime",
            value_keypath = ["pumps", pump_type, "runtime"],
            device_class = SensorDeviceClass.DURATION,
            state_class = SensorStateClass.TOTAL,
            unit_of_measurement = UnitOfTime.SECONDS,
        ),
    ]
