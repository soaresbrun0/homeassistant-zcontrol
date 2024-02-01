"""Data update coordinator for ZControl® integration."""

from datetime import timedelta
import logging

from pyzctrl.devices.basic import ZControlDevice
from pyzctrl.devices.connection import (
    ZControlDeviceConnection,
    ZControlDeviceHTTPConnection,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ZControlDataUpdateCoordinator(DataUpdateCoordinator):
    """The ZControl® data update coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: ZControlDevice,
        update_interval: timedelta,
    ) -> None:
        """Initialize the data update coordinator."""

        super().__init__(
            hass,
            _LOGGER,
            name = device.device_id,
            update_interval = update_interval,
        )
        self.device = device

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information for the device managed by this coordinator."""
        connection_url: str | None = None
        if isinstance(self.device.connection, ZControlDeviceHTTPConnection):
            connection_url = self.device.connection.base_url

        return DeviceInfo(
            identifiers = {(DOMAIN, self.device.device_id)},
            manufacturer = self.device.__class__.MANUFACTURER,
            model = self.device.__class__.MODEL,
            name = self.device.device_id,
            serial_number = self.device.serial_number,
            hw_version = self.device.firmware_version,
            configuration_url = connection_url,
        )

    async def _async_update_data(self) -> None:
        """Update device and return its attrributes."""

        try:
            await self.hass.async_add_executor_job(self.device.update)
        except ZControlDeviceConnection.ConnectionError as err:
            raise UpdateFailed(f"Error updating device: {err}") from err
