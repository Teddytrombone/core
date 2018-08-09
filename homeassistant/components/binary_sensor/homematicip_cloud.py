"""
Support for HomematicIP binary sensor.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/binary_sensor.homematicip_cloud/
"""

import logging

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.components.homematicip_cloud import (
    HomematicipGenericDevice, DOMAIN as HMIPC_DOMAIN,
    HMIPC_HAPID)

DEPENDENCIES = ['homematicip_cloud']

_LOGGER = logging.getLogger(__name__)

STATE_SMOKE_OFF = 'IDLE_OFF'


async def async_setup_platform(hass, config, async_add_devices,
                               discovery_info=None):
    """Set up the binary sensor devices."""
    pass


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the HomematicIP binary sensor from a config entry."""
    from homematicip.aio.device import (
        AsyncShutterContact, AsyncMotionDetectorIndoor, AsyncSmokeDetector)

    home = hass.data[HMIPC_DOMAIN][config_entry.data[HMIPC_HAPID]].home
    devices = []
    for device in home.devices:
        if isinstance(device, AsyncShutterContact):
            devices.append(HomematicipShutterContact(home, device))
        elif isinstance(device, AsyncMotionDetectorIndoor):
            devices.append(HomematicipMotionDetector(home, device))
        elif isinstance(device, AsyncSmokeDetector):
            devices.append(HomematicipSmokeDetector(home, device))

    if devices:
        async_add_devices(devices)


class HomematicipShutterContact(HomematicipGenericDevice, BinarySensorDevice):
    """HomematicIP shutter contact."""

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return 'door'

    @property
    def is_on(self):
        """Return true if the shutter contact is on/open."""
        from homematicip.base.enums import WindowState

        if self._device.sabotage:
            return True
        if self._device.windowState is None:
            return None
        return self._device.windowState == WindowState.OPEN


class HomematicipMotionDetector(HomematicipGenericDevice, BinarySensorDevice):
    """MomematicIP motion detector."""

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return 'motion'

    @property
    def is_on(self):
        """Return true if motion is detected."""
        if self._device.sabotage:
            return True
        return self._device.motionDetected


class HomematicipSmokeDetector(HomematicipGenericDevice, BinarySensorDevice):
    """MomematicIP smoke detector."""

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return 'smoke'

    @property
    def is_on(self):
        """Return true if smoke is detected."""
        return self._device.smokeDetectorAlarmType != STATE_SMOKE_OFF
