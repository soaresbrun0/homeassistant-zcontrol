"""Binary sensors for ZControl® integration."""

from typing import Any

from pyzctrl.devices.battery import ZControlBatteryDevice
from pyzctrl.devices.float import ZControlFloatDevice
from pyzctrl.devices.pump import ZControlPumpDevice

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ZControlDataUpdateCoordinator
from .entity import ZControlEntity


class ZControlBinarySensorEntity(ZControlEntity, BinarySensorEntity):
    """Represents a ZControl® binary sensor."""

    def _update_value(self, value: Any) -> None:
        self._attr_is_on = value is True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up ZControl® binary sensors for the given config entry."""
    coordinator: ZControlDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    device = coordinator.device
    binary_sensors: [BinarySensorEntity] = _create_basic_device_binary_sensors(coordinator)
    if isinstance(device, ZControlBatteryDevice):
        binary_sensors.extend(_create_battery_device_binary_sensors(device, coordinator))
    if isinstance(device, ZControlFloatDevice):
        binary_sensors.extend(_create_float_device_binary_sensors(device, coordinator))
    if isinstance(device, ZControlPumpDevice):
        binary_sensors.extend(_create_pump_device_binary_sensors(device, coordinator))
    async_add_entities(binary_sensors)


def _create_basic_device_binary_sensors(
    coordinator: ZControlDataUpdateCoordinator
) -> [ZControlBinarySensorEntity]:
    return [
        ZControlBinarySensorEntity(
            coordinator,
            value_keypath = ["is_self_test_running"],
            name = "Self-Test",
            device_class = BinarySensorDeviceClass.RUNNING
        ),
    ]

def _create_battery_device_binary_sensors(
    device: ZControlBatteryDevice,
    coordinator: ZControlDataUpdateCoordinator,
) -> [ZControlBinarySensorEntity]:
    binary_sensors = [
        ZControlBinarySensorEntity(
            coordinator,
            name = "Primary Power",
            value_keypath = ["is_primary_power_missing"],
            value_modifier = lambda v: not v if isinstance(v, bool) else v,
            device_class = BinarySensorDeviceClass.POWER
        ),
    ]
    for battery_type in device.batteries:
        binary_sensors.extend(_create_battery_binary_sensors(battery_type, coordinator))
    return binary_sensors

def _create_battery_binary_sensors(
    battery_type: ZControlBatteryDevice.Battery.Type,
    coordinator: ZControlDataUpdateCoordinator,
) -> [ZControlBinarySensorEntity]:
    battery_name = f"{battery_type.value} Battery"

    return [
        ZControlBinarySensorEntity(
            coordinator,
            battery_name,
            value_keypath = ["batteries", battery_type, "is_low"],
            device_class = BinarySensorDeviceClass.BATTERY
        ),
        ZControlBinarySensorEntity(
            coordinator,
            f"{battery_name} Charging",
            value_keypath = ["batteries", battery_type, "is_charging"],
            device_class = BinarySensorDeviceClass.BATTERY_CHARGING
        ),
        ZControlBinarySensorEntity(
            coordinator,
            f"{battery_name} Presence",
            value_keypath = ["batteries", battery_type, "is_missing"],
            device_class = BinarySensorDeviceClass.PROBLEM
        ),
        ZControlBinarySensorEntity(
            coordinator,
            f"{battery_name} Condition",
            value_keypath = ["batteries", battery_type, "is_bad"],
            device_class = BinarySensorDeviceClass.PROBLEM
        ),
    ]

def _create_float_device_binary_sensors(
    device: ZControlFloatDevice,
    coordinator: ZControlDataUpdateCoordinator,
) -> [ZControlBinarySensorEntity]:
    binary_sensors: [ZControlBinarySensorEntity] = []
    for float_type in device.floats:
        binary_sensors.extend(_create_float_binary_sensors(float_type, coordinator))
    return binary_sensors

def _create_float_binary_sensors(
    float_type: ZControlFloatDevice.Float.Type,
    coordinator: ZControlDataUpdateCoordinator,
) -> [ZControlBinarySensorEntity]:
    float_name = f"{float_type.value} Float"

    return [
         ZControlBinarySensorEntity(
            coordinator,
            float_name,
            value_keypath = ["floats", float_type, "is_active"],
            value_modifier = lambda v: not v if isinstance(v, bool) else v,
            device_class = BinarySensorDeviceClass.OPENING
        ),
        ZControlBinarySensorEntity(
            coordinator,
            f"{float_name} Presence",
            value_keypath = ["floats", float_type, "is_missing"],
            device_class = BinarySensorDeviceClass.PROBLEM
        ),
        ZControlBinarySensorEntity(
            coordinator,
            f"{float_name} All-Time Presence",
            value_keypath = ["floats", float_type, "never_present"],
            device_class = BinarySensorDeviceClass.PROBLEM
        ),
        ZControlBinarySensorEntity(
            coordinator,
            f"{float_name} Condition",
            value_keypath = ["floats", float_type, "is_malfunctioning"],
            device_class = BinarySensorDeviceClass.PROBLEM
        ),
    ]

def _create_pump_device_binary_sensors(
    device: ZControlPumpDevice,
    coordinator: ZControlDataUpdateCoordinator,
) -> [ZControlBinarySensorEntity]:
    binary_sensors: [ZControlBinarySensorEntity] = []
    for pump_type in device.pumps:
        binary_sensors.extend(_create_pump_binary_sensors(pump_type, coordinator))
    return binary_sensors

def _create_pump_binary_sensors(
    pump_type: ZControlPumpDevice.Pump.Type,
    coordinator: ZControlDataUpdateCoordinator,
) -> [ZControlBinarySensorEntity]:
    pump_name = f"{pump_type.value} Pump"

    return [
        ZControlBinarySensorEntity(
            coordinator,
            pump_name,
            value_keypath = ["pumps", pump_type, "is_running"],
            device_class = BinarySensorDeviceClass.RUNNING
        ),
        ZControlBinarySensorEntity(
            coordinator,
            f"{pump_name} Airlock",
            value_keypath = ["pumps", pump_type, "airlock_detected"],
            device_class = BinarySensorDeviceClass.PROBLEM
        ),
    ]
