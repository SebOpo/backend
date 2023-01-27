from typing import TypeVar, Generic, Type, List

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        pass

    def get(self, db: Session, model_id: int) -> ModelType:
        return db.query(self.model).get(model_id)

    def get_all(self, db: Session) -> List[ModelType]:
        return db.query(self.model).all()

    def get_many(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def delete(self, db: Session, model_id: int) -> None:
        model = self.get(db, model_id=model_id)
        db.delete(model)
        db.commit()
        return None
