"""Python wrapper functions around the Warmup HTTP API"""

import logging
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple

import requests
from pywarmup.error import APIError
from pywarmup.error import InvalidToken
from pywarmup.error import LocationModeChangeFailure
from pywarmup.error import TemperatureChangeFailure

TOKEN_URL = "https://api.warmup.com/apps/app/v1"
URL = "https://apil.warmup.com/graphql"
APP_TOKEN = 'M=;He<Xtg"$}4N%5k{$:PD+WA"]D<;#PriteY|VTuA>_iyhs+vA"4lic{6-LqNM:'
HEADER = {
    "user-agent": "WARMUP_APP",
    "accept-encoding": "br, gzip, deflate",
    "accept": "*/*",
    "Connection": "keep-alive",
    "content-type": "application/json",
    "app-token": APP_TOKEN,
    "app-version": "1.8.1",
    "accept-language": "de-de",
}

_LOG = logging.getLogger(__name__)


class TemperatureUnit(Enum):
    CELSIUS = "C"
    FAHRENHEIT = "F"


class LocationMode(Enum):
    ON = "ON"
    OFF = "OFF"


class Location(NamedTuple):
    id: int
    name: str
    temp_unit: TemperatureUnit
    mode: LocationMode


class ProgramMode(Enum):
    PROGRAM = "program"
    FIXED = "fixed"
    OFF = "off"


class Room(NamedTuple):
    id: int
    name: str
    mode: ProgramMode
    run_mode: int
    current_temp: float
    target_temp: float
    target_temp_low: float
    target_temp_high: float
    override_duration: int
    override_temp: float
    location: Location


def get_access_token(email: str, password: str) -> str:
    body = {
        "request": {
            "email": email,
            "password": password,
            "method": "userLogin",
            "appId": "WARMUP-APP-V001",
        }
    }
    response = requests.post(url=TOKEN_URL, headers=HEADER, json=body)
    status = response.json()["status"]

    if response.status_code != 200 or status["result"] != "success":
        if "message" in response.json():
            _LOG.info(
                "Failed to retrieve token. Response: %s", response.json()["message"]
            )
        raise InvalidToken
    return str(response.json()["response"]["token"])


class API:
    """API object wrapping the Warmup REST API."""

    def __init__(self, email: str, access_token: str):
        self.email = email
        self.access_token = access_token

    def get_locations(self) -> List[Location]:
        """Get all available locations."""
        request = {"method": "getLocations"}
        response = self._send_request(request)
        locations = response["locations"]
        result = []
        for location in locations:
            result.append(
                Location(
                    id=location["id"],
                    name=location["name"],
                    temp_unit=TemperatureUnit.CELSIUS,
                    mode=LocationMode.OFF
                    if location["locMode"] == "off"
                    else LocationMode.ON,
                )
            )
        return result

    def get_location(self, location_id: int) -> Location:
        """Get location information for the specified location."""
        # FIXME this is pretty inefficient. We should send a query just for the location
        locations = self.get_locations()
        location = next((x for x in locations if x.id == location_id), None)
        if location is None:
            _LOG.info("No such location: %d", location_id)
            raise APIError
        return location

    def get_rooms(self) -> List[Room]:
        """Retrieve all rooms for this account."""
        body = {
            "query": "query QUERY { user { currentLocation: location { id name rooms "
            "{ id roomName roomMode runModeInt targetTemp currentTemp "
            "overrideDur overrideTemp "
            "thermostat4ies {minTemp maxTemp}}}}} "
        }
        header_with_token = HEADER.copy()
        header_with_token["warmup-authorization"] = self.access_token
        response = requests.post(url=URL, headers=header_with_token, json=body)
        if response.status_code != 200 or response.json()["status"] != "success":
            _LOG.info("Failed get room data: %s", response)
            raise APIError

        rooms = response.json()["data"]["user"]["currentLocation"]["rooms"]
        location = response.json()["data"]["user"]["currentLocation"]
        location = self.get_location(location["id"])
        result = []
        for room in rooms:
            result.append(
                Room(
                    id=room["id"],
                    name=room["roomName"],
                    mode=ProgramMode.PROGRAM
                    if room["roomMode"] == "program"
                    else ProgramMode.FIXED,
                    run_mode=room["runModeInt"],
                    current_temp=room["currentTemp"] / 10,
                    target_temp=room["targetTemp"] / 10,
                    target_temp_low=room["thermostat4ies"][0]["minTemp"] / 10,
                    target_temp_high=room["thermostat4ies"][0]["maxTemp"] / 10,
                    override_duration=room["overrideDur"],
                    override_temp=room["overrideTemp"] / 10,
                    location=location,
                )
            )
        return result

    def get_room(self, room_id: int) -> Room:
        """Get information on the specified room."""
        """Get information for a specific room."""
        # FIXME this is pretty inefficient. We should send a query just for the room.
        rooms = self.get_rooms()
        room = next((x for x in rooms if x.id == room_id), None)
        if room is None:
            _LOG.info("No such room: %d", room_id)
            raise APIError
        return room

    def set_temperature(self, room_id: int, new_temperature: float) -> None:
        """Set the specified room's temperature."""
        body = {
            "account": {"email": self.email, "token": self.access_token},
            "request": {
                "method": "setProgramme",
                "roomId": room_id,
                "roomMode": "fixed",
                "fixed": {"fixedTemp": "{:03d}".format(int(new_temperature * 10))},
            },
        }
        _LOG.info("Setting new target temperature: %s", new_temperature)
        response = requests.post(url=TOKEN_URL, headers=HEADER, json=body)

        if (
            response.status_code != 200
            or response.json()["status"]["result"] != "success"
        ):
            _LOG.info("Setting new target temperature failed: %s", response)
            raise TemperatureChangeFailure

    def set_location_to_frost(self, location_id: int) -> None:
        """Set the specified location to frost preset."""
        request = {
            "method": "setModes",
            "values": {
                "locId": location_id,
                "holEnd": "-",
                "fixedTemp": "",
                "holStart": "-",
                "geoMode": "0",
                "holTemp": "-",
                "locMode": "frost",
            },
        }

        self._send_request(request)
        _LOG.info(
            "Successfully set location: %d to frost protection", location_id,
        )

    def set_temperature_to_auto(self, room_id: int) -> None:
        """Set temperature control to automatic for the given room."""
        request = {"method": "setProgramme", "roomId": room_id, "roomMode": "prog"}
        self._send_request(request)
        _LOG.info("Successfully set room %d to auto", room_id)

    def set_temperature_to_manual(self, room_id: int) -> None:
        """Set temperature control to manual for the given room."""
        request = {"method": "setProgramme", "roomId": room_id, "roomMode": "fixed"}
        self._send_request(request)
        _LOG.info("Successfully set room %d to manual", room_id)

    def set_location_to_off(self, location_id: int) -> None:
        """Turn off device at specified location."""
        request = {
            "method": "setModes",
            "values": {
                "holEnd": "-",
                "fixedTemp": "",
                "holStart": "-",
                "geoMode": "0",
                "holTemp": "-",
                "locId": location_id,
                "locMode": "off",
            },
        }
        self._send_request(request)

    def _send_request(self, request: Dict[str, Any]) -> Dict:
        body = {
            "account": {"email": self.email, "token": self.access_token},
            "request": request,
        }
        response = requests.post(url=TOKEN_URL, headers=HEADER, json=body)
        if (
            response.status_code != 200
            or response.json()["status"]["result"] != "success"
        ):
            _LOG.info("Failed to send request. Response:", response)
            raise LocationModeChangeFailure

        return dict(response.json().get("response"))
