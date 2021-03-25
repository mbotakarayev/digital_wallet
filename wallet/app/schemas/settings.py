from pydantic.main import BaseModel


class Country(BaseModel):
    id: int
    iso_code: str
    country_code: int

    class Config:
        orm_mode = True
