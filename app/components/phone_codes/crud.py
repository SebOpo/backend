import logging
from typing import List

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.base_crud import CRUDBase
from app.components import phone_codes

logger = logging.getLogger(settings.PROJECT_NAME)


class CRUDPhoneCode(
    CRUDBase[
        phone_codes.models.PhoneCode,
        phone_codes.schemas.PhoneCodeOut,
        phone_codes.schemas.PhoneCodeOut,
    ]
):
    def get_list(self, db: Session):
        return db.query(self.model).filter(self.model.is_active == True).all()


codes = CRUDPhoneCode(phone_codes.models.PhoneCode)
