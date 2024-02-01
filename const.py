"""Constants for ZControl® integration."""

from pyzctrl.devices.aquanot import AquanotFit508
from pyzctrl.devices.connection import ZControlDeviceHTTPConnection

DOMAIN = "zcontrol"
DEFAULT_TIMEOUT = ZControlDeviceHTTPConnection.DEFAULT_TIMEOUT
DEFAULT_SCAN_INTERVAL = 5

SUPPORTED_DEVICES_BY_MODEL = {
    AquanotFit508.MODEL: AquanotFit508
}
