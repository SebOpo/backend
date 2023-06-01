from pydantic import BaseModel


class PhoneCodeOut(BaseModel):
    id: int
    country_code: str
    verbose_name: str
    phone_code: str

    class Config:
        orm_mode = True
