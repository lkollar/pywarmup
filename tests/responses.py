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
