import io
import logging
from enum import Enum
from typing import Optional

from .tuya_vacuum_map_extractor import get_map

from homeassistant.components.camera import (
    Camera,
    ENTITY_ID_FORMAT,
    CameraEntityFeature,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.const import (
    CONF_NAME,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_DEVICE_ID,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config, async_add_entities, discovery_info=None):
    _LOGGER.debug("Async setup entry")
    name = config.title
    should_poll = False
    entity_id = generate_entity_id(ENTITY_ID_FORMAT, name, hass=hass)
    server = config.data["server"]
    client_id = config.data["client_id"]
    secret_key = config.data["client_secret"]
    device_id = config.data["device_id"]
    _LOGGER.debug("Adding entities")
    async_add_entities(
        [
            VacuumCamera(
                entity_id, name, server, client_id, secret_key, device_id, should_poll
            )
        ]
    )
    _LOGGER.debug("Done")


class VacuumCamera(Camera):
    def __init__(
        self,
        entity_id: str,
        name: str,
        server: str,
        client_id: str,
        secret_key: str,
        device_id: str,
        should_poll: bool,
    ) -> None:
        """Initialized camera."""
        _LOGGER.debug("Init camera")
        super().__init__()
        self.entity_id = entity_id
        self.content_type = "image/png"
        self._status = CameraStatus.INITIALIZING
        self._device = None
        self._attr_name = name
        self._server = server
        self._access_token = ""
        self._should_poll = should_poll
        self._image = None
        self._map_data = None
        self._client_id = client_id
        self._secret_key = secret_key
        self._device_id = device_id
        self._attr_unique_id = client_id + device_id

    async def async_added_to_hass(self) -> None:
        self.async_schedule_update_ha_state(True)

    @property
    def supported_features(self) -> int:
        return CameraEntityFeature.ON_OFF

    @property
    def should_poll(self) -> bool:
        return self._should_poll

    @property
    def frame_interval(self) -> float:
        return 1

    @property
    def state(self) -> str:
        _LOGGER.debug("Fetching state")
        if self._should_poll == True:
            if self._status == CameraStatus.OK:
                return "on"
            if self._status == CameraStatus.FAILURE:
                return "error"
            else:
                return "unknown"
        else:
            return "off"

    def update(self):
        try:
            _LOGGER.debug("Getting map")
            map_data = get_map(
                self._server, self._client_id, self._secret_key, self._device_id
            )
            _LOGGER.debug("Map data retrieved")
        except Exception as error:
            _LOGGER.warning("Unable to parse map data")
            _LOGGER.error(error)
            self._status = CameraStatus.FAILURE
            return

        if map_data is not None:
            _LOGGER.debug("Map is ok")
            self._set_map_data(map_data)
            self._status = CameraStatus.OK

    def _set_map_data(self, map_data):
        img_byte_arr = io.BytesIO()
        map_data.save(img_byte_arr, format="PNG")
        self._image = img_byte_arr.getvalue()
        self._map_data = map_data

    def camera_image(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> Optional[bytes]:
        return self._image

    def turn_on(self):
        self._should_poll = True

    def turn_off(self):
        self._should_poll = False


class CameraStatus(Enum):
    INITIALIZING = "Initializing"
    OK = "OK"
    FAILURE = "Faliure"
