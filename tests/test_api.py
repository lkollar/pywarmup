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

from .responses import RESPONSE_GET_LOCATIONS
from .responses import RESPONSE_GET_ROOM_DATA
from .responses import RESPONSE_GET_TOKEN
from .responses import RESPONSE_SET_TEMPERATURE


@pytest.fixture
def api_factory():
    return API(email="", access_token="")


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


@patch("pywarmup.api.requests")
class TestAPI:
    def test_get_locations(self, requests_mock, api_factory):
        api = api_factory
        requests_mock.post.return_value = Mock(
            **{"json.return_value": RESPONSE_GET_LOCATIONS, "status_code": 200}
        )
        locations = api.get_locations()
        assert len(locations) == 1
        assert locations[0].id == 123
        assert locations[0].name == "Home"

    def test_get_room_data(self, requests_mock, api_factory):
        api = api_factory
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
                id=123,
                name="Home",
                temp_unit=TemperatureUnit.CELSIUS,
                mode=LocationMode.ON,
            ),
        )

    def test_get_room(self, requests_mock, api_factory):
        api = api_factory
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

    def test_set_temperature(self, requests_mock, api_factory):
        api = api_factory

        requests_mock.post.return_value = Mock(
            **{"json.return_value": RESPONSE_SET_TEMPERATURE, "status_code": 200}
        )

        # No exception should be raised
        api.set_temperature(room_id=64188, new_temperature=18.0)
        api.set_temperature_to_auto(room_id=64188)
        api.set_temperature_to_manual(room_id=64188)

    def test_set_location_to_frost(self, requests_mock, api_factory):
        api = api_factory

        requests_mock.post.return_value = Mock(
            **{
                "json.return_value": {
                    "status": {"result": "success"},
                    "message": {"duration": "0.543"},
                },
                "status_code": 200,
            }
        )

        # No exception should be raised
        api.set_location_to_frost(location_id=123)
