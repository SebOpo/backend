import datetime
from typing import Optional

from app.utils.time_utils import utc_convert


def convert_to_utc(timestamp: datetime.datetime) -> Optional[str]:
    if not timestamp:
        return None
    return utc_convert(timestamp)
