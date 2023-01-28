from typing import Any, Optional, Dict

from geopy.geocoders import GoogleV3, Nominatim
import osmnx as ox
from shapely.geometry import Point

from app.core.config import settings


"""
We can use either of these providers to get the desired result.

Nominatim is powered by OSM (OpenStreetMaps) and is free, but has a rate-limiter by default, so all of the operations
will take more time to complete. It does not require an API key, you can specify the user_agent param as you wish.

GoogleV3 geocoder requires a valid API_KEY, spends the key's quota, but is usually faster and better works with the
frontend map, as it uses Gmaps as well.

Please note, that when trying to query the info about less populated areas (villages, suburbs), OSM usually has more
info about that address than Google.

Currently , we use Google for geocoding and OSM for reverse geocoding.
"""

osm_geocoder = Nominatim(user_agent="GetLoc")
gmaps_geocoder = GoogleV3(api_key=settings.GMAPS_APIKEY)


def geocode_address(
        address: str,
        city: str,
        region: str = 'ua'
) -> Any:

    """
    Takes an address string (can add more precision with city and region) to return its coordinates

    :param str address: Address of the desired location, can either be a street name or a street name with a house num
    :param str city: City of the desired address, any language (local/english) is supported
    :param str region: Short alias for the region name to add more precision to the search
    :return: Desired address coordinates or None if not found.
    """

    try:
        coordinates = gmaps_geocoder.geocode('{}, {}'.format(address, city), region=region)
        return coordinates

    except Exception as e:
        print(e)
        return None


def reverse(
        lat: float,
        lng: float,
        geocoding_service: str = "osm"
) -> Optional[Dict]:

    """
    Takes the coordinates of a location to return its address information from the chosen provider or None if this info
    cannot be obtained.

    :param float lat: Latitude of an address
    :param float lng: Longitude of an address
    :param geocoding_service: the abbreviation for the geocoder to use
    :return: Address object from the chosen provider
    Example : {
        'house_number': '64',
        'road': 'Стеценка вулиця',
        'suburb': 'Замостя',
        'city': 'Вінниця',
        'municipality': 'Вінницька міська громада',
        'district': 'Вінницький район',
        'state': 'Вінницька область',
        'ISO3166-2-lvl4': 'UA-05',
        'postcode': '21009',
        'country': 'Україна',
        'country_code': 'ua'
    }

    """
    # TODO ADD GMAPS geocoder support
    if geocoding_service == "osm":
        geocoder = osm_geocoder
    elif geocoding_service == "gmaps":
        # Those options do not really affect anything because the support for gmaps geocoder is still in dev.
        # This is hardcoded so frontend does not encounter any errors.
        geocoder = osm_geocoder
    else:
        geocoder = osm_geocoder

    try:
        address = geocoder.reverse('{}, {}'.format(lat, lng))
        return address.raw["address"]

    except Exception as e:
        print(e)
        return None


def get_bounding_box_by_region_name(region_name: str):

    """
    This method takes a region name ( Could be a Country/City/Administrative area/Village etc. or even a street name )
    to return a bounding box of this object represented by geometrical points (Either a Polygon or a Multipolygon for
    complex locations).

    :param str region_name: Name of an object (Country/City/Administrative area etc.) in any language (local/english).
    :return: A Polygon or a Multipolygon type object representing the area's bounding box or None if none was found.
    """

    try:
        gdf = ox.geocode_to_gdf(region_name)
        geom = gdf.loc[0, 'geometry']
        return geom

    except ValueError:
        return None


def check_intersection(
        geom: Any,
        coords: tuple
) -> bool:
    """
    This method takes an area represented by a shape and a coordinates point to check if the point is present
    in an area.

    Throughout the app we are using it to check if the newly requested location address doesn't intersect with the
    areas in which the reports are restricted (Crimea for example at the time of writing, as it is temporarily occupied
    by russia.)

    :param geom: This should be a geometrical object (Shape, mostly Polygon or Multipolygon) representing the bounding
     box of an area we check the intersection with
    :param tuple coords: A tuple of coordinates of a location which we try to fit in our geom.
     Example: (49.271511, 28.19311)
    :return: A boolean which represents if the coordinates actually intersect with our geom.
    """

    return geom.intersects(Point(coords))

