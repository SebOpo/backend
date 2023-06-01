from typing import Any
import logging

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

from app.components.phone_codes import schemas, crud
from app.api.dependencies import get_db, get_current_active_user
from app.core.config import settings

logger = logging.getLogger(settings.PROJECT_NAME)


router = APIRouter(prefix="/phone-codes", tags=["phone-codes"])


@router.get('/all', response_model=schemas.PhoneCodeOut)
async def get_all_phone_codes(
        db: Session = Depends(get_db)
) -> Any:
    try:
        code_list = crud.codes.get_list(db)
        return code_list
    except Exception as e:
        logger.error('Encountered an error in /phone-codes/all : {}'.format(e))
        raise HTTPException(status_code=500, detail="Db error, please try again.")