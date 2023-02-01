import random

from app.components.reports import enums


def get_random_enum_choice(enum):
    return random.choice(enum.list())


def populate_reports():
    return {
        "buildingCondition": {
            "flag": get_random_enum_choice(enums.BuildingConditionEnum),
            "description": "",
        },
        "electricity": {
            "flag": get_random_enum_choice(enums.ElectricityEnum),
            "description": "",
        },
        "carEntrance": {
            "flag": get_random_enum_choice(enums.CarEntranceEnum),
            "description": "",
        },
        "water": {"flag": get_random_enum_choice(enums.WaterEnum), "description": ""},
        "fuelStation": {
            "flag": get_random_enum_choice(enums.FuelStationEnum),
            "description": "",
            "distance": random.uniform(0.1, 9.9),
        },
        "hospital": {
            "flag": get_random_enum_choice(enums.HospitalEnum),
            "description": "",
            "distance": random.uniform(0.1, 9.9),
        },
    }
