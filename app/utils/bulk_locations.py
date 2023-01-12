from typing import List, Dict, Generator
import logging

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from sqlalchemy.orm import Session

from app.utils.geocoding import geocode_address
from app.db.session import SessionLocal
from app.models.location import Location
from app.crud.crud_geospatial import create_index
from app.crud.crud_user import get_by_email
from app.schemas.location import LocationReports
from app.core.config import settings
from app.crud.crud_location import get_location_by_coordinates, submit_location_reports


logger = logging.getLogger(settings.PROJECT_NAME)


def serialize_spreadsheet(spreadsheet, sheet_type: int) -> List[Dict]:
    locations = []
    if sheet_type == 1:
        for row in spreadsheet.iter_rows(min_row=2, min_col=2):
            if row[0].value is None:
                continue
            location = {
                "address": row[0].value,
                "city": row[1].value,
                "country": row[2].value,
                "index": row[3].value,
                "reports": {
                    "buildingCondition": {
                        "flag": row[4].value.lower(),
                        "description": row[10].value if row[10].value else ""
                    },
                    "electricity": {
                        "flag": row[5].value.lower(),
                        "description": ""
                    },
                    "carEntrance": {
                        "flag": row[6].value.lower(),
                        "description": ""
                    },
                    "water": {
                        "flag": row[7].value.lower(),
                        "description": ""
                    },
                    "fuelStation": {
                        "flag": row[8].value.lower(),
                        "description": ""
                    },
                    "hospital": {
                        "flag": row[9].value.lower(),
                        "description": ""
                    }
                }
            }
            if location["address"] is None:
                continue
            locations.append(location)

    elif sheet_type == 2:
        for row in spreadsheet.iter_rows(min_row=2, min_col=1):
            if row[0].value is None:
                continue
            location = {
                "address": row[0].value,
                "street_number": int(row[1].value) if isinstance(row[1].value, float) else row[1].value,
                "city": row[2].value,
                "country": row[3].value,
                "index": row[4].value,
                "reports": {
                    "buildingCondition": {
                        "flag": row[5].value.lower(),
                        "description": row[11].value if row[11].value else ""
                    },
                    "electricity": {
                        "flag": row[6].value.lower(),
                        "description": ""
                    },
                    "carEntrance": {
                        "flag": row[7].value.lower(),
                        "description": ""
                    },
                    "water": {
                        "flag": row[8].value.lower(),
                        "description": ""
                    },
                    "fuelStation": {
                        "flag": row[9].value.lower(),
                        "description": ""
                    },
                    "hospital": {
                        "flag": row[10].value.lower(),
                        "description": ""
                    }
                }
            }
            if location["address"] is None:
                continue
            locations.append(location)
    return locations


# def geocode_locations(locations: List[Dict]):
#
#     geocoded_locations = []
#     for location in locations:
#         addr_str = '{}'.format(location["address"] + " " + str(location.get('street_number')) if location.get('street_number',None) else location["address"])
#         coordinates = geocode_address(addr_str, location["city"])
#         if not coordinates:
#             continue
#         location["lat"] = coordinates.latitude
#         location["lng"] = coordinates.longitude
#         geocoded_locations.append(location)
#
#     return geocoded_locations


def add_to_db(location):
    try:
        db: Session = SessionLocal()
        existing_location = get_location_by_coordinates(db, lat=location.get('lat'), lng=location.get('lng'))
        if existing_location:
            return None
        reporting_user = get_by_email(db, email=settings.FIRST_SUPERUSER)
        db_obj = Location(
            address=location.get('address'),
            index=location.get('index'),
            lat=location.get('lat'),
            lng=location.get('lng'),
            country=location.get('country'),
            city=location.get('city'),
            status=3,
            reports=location.get('reports'),
            street_number=location.get('street_number', None)
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        index = create_index(db, location_id=db_obj.id, lat=db_obj.lat, lng=db_obj.lng, status=db_obj.status)

        submit_location_reports(
            db,
            obj_in=LocationReports(location_id=db_obj.id, **location.get('reports')),
            user_id=reporting_user.id
        )

        db.close()

        return db_obj

    except Exception as e:
        print(e)
        return None


def bulk_create(spreadsheet_path: str, sheet_type: int):
    try:

        wb2 = load_workbook(spreadsheet_path)
        sheet = wb2.active
        locations = serialize_spreadsheet(sheet, sheet_type=sheet_type)
        print('Finished serializing, total locations {}'.format(len(locations)))
        updated_locations = geocode_locations(locations)
        print('Finished geocoding, total locations {}'.format(len(updated_locations)))
        unregistered_locations = []
        for location in updated_locations:
            if not location.get('lat') or not location.get('lng'):
                continue
            loc = add_to_db(location)
            if not loc:
                unregistered_locations.append(location)

        print('Could not register {} locations.'.format(len(unregistered_locations)))

        return unregistered_locations

    except Exception as e:
        print(e)
        return None


async def serialize_excel(
    spreadsheet: Worksheet
) -> Dict:
    locations = []
    unprocessed_locations = []
    for row in spreadsheet.iter_rows(values_only=True):
        if not row[0]:
            continue
        try:
            location = {
                "address": row[0].strip(),
                "street_number": row[1],
                "city": row[2],
                "country": row[3],
                "postcode": row[4],
                "reports": {
                    "buildingCondition": {
                        "flag": row[5],
                        "description": row[11] if row[11] else ""
                    },
                    "electricity": {
                        "flag": row[6],
                        "description": ""
                    },
                    "carEntrance": {
                        "flag": row[7],
                        "description": ""
                    },
                    "water": {
                        "flag": row[8],
                        "description": ""
                    },
                    "fuelStation": {
                        "flag": row[9],
                        "description": ""
                    },
                    "pharmacy": {
                        "flag": row[10],
                        "description": ""
                    }
                }
            }
            locations.append(location)

        except Exception as e:
            unprocessed_locations.append({
                "location": row,
                "code": "SERIALIZATION_ERROR",
                "detail": e
            })

    return {
        "processed": locations,
        "unprocessed": unprocessed_locations
    }


async def geocode_locations(
    locations: List[Dict]
) -> Dict:

    geocoded_locations = []
    unprocessed_locations = []
    for location in locations:
        address_string = "{}, {}".format(location.get('address'), location.get('street_number'))
        coordinates = geocode_address(
            address=address_string,
            city=location.get('city')
        )
        if not coordinates:
            unprocessed_locations.append({
                "location": location,
                "code": "GEOCODING_ERROR",
                "detail": "Address not found"
            })
            continue
        location["lat"] = coordinates.latitude
        location["lng"] = coordinates.longitude
        geocoded_locations.append(location)

    return {
        "geocoded": geocoded_locations,
        "unprocessed": unprocessed_locations
    }


async def upload_locations(
        filepath: str,
        doctype: str
):

    unprocessed_locations = []

    if doctype == "excel":
        workbook = load_workbook(filepath)
        sheet = workbook.active
        logger.debug("XLSX loaded, starting serialization.")

        serialization_results = await serialize_excel(sheet)
        unprocessed_locations = serialization_results.get('unprocessed')
        serialized_locations = serialization_results.get('processed')
        logger.debug("Processed locations: {}".format(len(serialized_locations)))
        logger.debug("Unprocessed locations: {}".format(len(unprocessed_locations)))

        logger.debug("Starting geocoding")
        geocoding_results = await geocode_locations(serialized_locations)
        geocoded_locations = geocoding_results.get('geocoded')
        unprocessed_locations.append(loc for loc in geocoding_results.get('unprocessed'))
        logger.debug("Geocoded locations: {}".format(len(geocoded_locations)))
        logger.debug("Could not geocode: {}".format(len(geocoding_results.get('unprocessed'))))

        logger.debug("Adding {} locations to database".format(len(geocoded_locations)))

        return unprocessed_locations

