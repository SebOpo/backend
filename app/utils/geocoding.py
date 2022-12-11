from typing import Any

from geopy.geocoders import GoogleV3, Nominatim

# TODO REMOVE APIKEY TO ENV
# loc = GoogleV3(api_key="AIzaSyBmAcISYICCUrXDzJAkhxCPcvF0hkn6iUo")
geocoder = Nominatim(user_agent="GetLoc")


def reverse(lat: float, lng: float) -> Any:

    try:
        address = geocoder.reverse('{}, {}'.format(lat, lng))
        # print(address)
        print(address.raw)
        return address.raw["address"]

    except Exception as e:
        print(e)
        return None
