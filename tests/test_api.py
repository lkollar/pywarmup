from unittest.mock import Mock
from unittest.mock import patch

import pytest

from pywarmup.api import API
from pywarmup.api import Location
from pywarmup.api import LocationMode
from pywarmup.api import ProgramMode
from pywarmup.api import Room
from pywarmup.api import TemperatureUnit
from pywarmup.api import get_access_token
from pywarmup.error import InvalidToken

RESPONSE_GET_TOKEN = {
    "status": {"result": "success"},
    "response": {
        "method": "userLogin",
        "token": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "mobileName": None,
    },
    "message": {"duration": "0.081"},
}

RESPONSE_GET_LOCATIONS = {
    "status": {"result": "success"},
    "response": {
        "method": "getLocations",
        "locations": [
            {
                "id": 123,
                "name": "Home",
                "latitude": "50.0",
                "longitude": "0.0",
                "countryCode": "GB",
                "timezone": "Europe/London",
                "currency": 0,
                "tempFormat": False,
                "smartGeo": False,
                "locZone": 0,
                "locMode": "notgeo",
                "holStart": None,
                "holEnd": None,
                "holTemp": 0,
                "zone": 0,
                "zoneOffset": "0.00",
                "zoneDirection": False,
                "zoneTime": 0,
                "mainRoom": None,
                "geoMode": 0,
                "now": "201912201459",
                "fenceArray": [150, 333, 1666, 5000, 10000, 20000],
            }
        ],
    },
    "message": {
        "getLocations": {
            "result": {
                "data": {
                    "user": {
                        "id": 1234,
                        "locations": [
                            {
                                "id": 123,
                                "name": "Home",
                                "geoLocation": {
                                    "latitude": "50.0",
                                    "longitude": "0.0",
                                },
                                "holiday": {
                                    "holStart": None,
                                    "holEnd": None,
                                    "holTemp": 0,
                                },
                                "address": {
                                    "owmCityId": 3333147,
                                    "countryCode": "GB",
                                    "timezone": "Europe/London",
                                    "currency": 0,
                                    "address1": "1 Long Road",
                                    "address2": "",
                                    "town": "London",
                                    "postcode": "EC1 XXX",
                                },
                                "locZone": {
                                    "zone": 0,
                                    "offset": "0.00",
                                    "isHoming": False,
                                    "time": "1970-01-01 00:00:00",
                                },
                                "settings": {
                                    "mainRoom": None,
                                    "isFahrenheit": False,
                                    "isSmartGeo": False,
                                },
                                "locMode": "not_geo",
                                "locModeInt": 1,
                                "fenceArray": [150, 333, 1666, 5000, 10000, 20000],
                                "geoModeInt": 0,
                            }
                        ],
                    }
                },
                "status": "success",
            }
        },
        "duration": "0.064",
    },
}

RESPONSE_GET_ROOM_DATA = {
    "data": {
        "user": {
            "currentLocation": {
                "id": 123,
                "name": "Home",
                "rooms": [
                    {
                        "id": 64188,
                        "roomName": "Bathroom",
                        "roomMode": "fixed",
                        "runModeInt": 3,
                        "targetTemp": 180,
                        "currentTemp": 205,
                        "overrideDur": 0,
                        "overrideTemp": 240,
                        "thermostat4ies": [{"minTemp": 50, "maxTemp": 300}],
                    }
                ],
            }
        }
    },
    "status": "success",
}

RESPONSE_SET_TEMPERATURE = {
    "status": {"result": "success"},
    "response": {
        "method": "setProgramme",
        "roomId": "64188",
        "type": "fixed",
        "roomMode": "fixed",
    },
    "message": {
        "setProgramme": {"roomModeUpdate": "3"},
        "targetTemp": "180",
        "checkLastRoomLocation": {
            "locId": "123",
            "locMode": "on",
            "deviceId": "64188",
            "runMode": 3,
            "misMatch": False,
        },
        "lastRoomLocationUpdated": False,
        "duration": "0.030",
    },
}


@pytest.fixture
@patch("pywarmup.api.requests")
def api_factory(requests_mock):
    api = API(email="", access_token="")
    return api, requests_mock


@patch("pywarmup.api.requests")
def test_get_token(requests_mock):
    requests_mock.post.return_value = Mock(
        **{"json.return_value": RESPONSE_GET_TOKEN, "status_code": 200}
    )
    token = get_access_token(email="", password="")
    assert token == "a" * 64


@patch("pywarmup.api.requests")
def test_get_token_http_error(requests_mock):
    requests_mock.post.return_value = Mock(
        **{"json.return_value": RESPONSE_GET_TOKEN, "status_code": 404}
    )
    with pytest.raises(InvalidToken):
        get_access_token(email="", password="")


def test_get_locations(api_factory):
    api, requests_mock = api_factory

    requests_mock.post.return_value = Mock(
        **{"json.return_value": RESPONSE_GET_LOCATIONS, "status_code": 200}
    )
    locations = api.get_locations()
    assert len(locations) == 1
    assert locations[0].id == 123
    assert locations[0].name == "Home"


def test_get_room_data(api_factory):
    api, requests_mock = api_factory
    requests_mock.post.side_effect = (
        Mock(**{"json.return_value": RESPONSE_GET_ROOM_DATA, "status_code": 200}),
        Mock(**{"json.return_value": RESPONSE_GET_LOCATIONS, "status_code": 200}),
    )
    rooms = api.get_rooms()
    assert len(rooms) == 1
    room = rooms[0]
    assert room == Room(
        id=64188,
        name="Bathroom",
        mode=ProgramMode.FIXED,
        run_mode=3,
        current_temp=20.5,
        target_temp=18.0,
        target_temp_low=5.0,
        target_temp_high=30.0,
        override_duration=0,
        override_temp=24.0,
        location=Location(
            id=123, name="Home", temp_unit=TemperatureUnit.CELSIUS, mode=LocationMode.ON
        ),
    )


def test_get_room(api_factory):
    api, requests_mock = api_factory
    requests_mock.post.side_effect = (
        Mock(**{"json.return_value": RESPONSE_GET_ROOM_DATA, "status_code": 200}),
        Mock(**{"json.return_value": RESPONSE_GET_LOCATIONS, "status_code": 200}),
    )
    room = api.get_room(room_id=64188)
    assert room == Room(
        id=64188,
        name="Bathroom",
        mode=ProgramMode.FIXED,
        run_mode=3,
        current_temp=20.5,
        target_temp=18.0,
        target_temp_low=5.0,
        target_temp_high=30.0,
        override_duration=0,
        override_temp=24.0,
        location=Location(
            id=123,
            name="Home",
            temp_unit=TemperatureUnit.CELSIUS,
            mode=LocationMode.ON,
        ),
    )


def test_set_temperature(api_factory):
    api, requests_mock = api_factory

    requests_mock.post.return_value = Mock(
        **{"json.return_value": RESPONSE_SET_TEMPERATURE, "status_code": 200}
    )

    # No exception should be raised
    api.set_temperature(room_id=64188, new_temperature=18.0)
    api.set_temperature_to_auto(room_id=64188)
    api.set_temperature_to_manual(room_id=64188)
