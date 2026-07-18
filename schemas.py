from pydantic import BaseModel


class PersonSchema(BaseModel):
    name: str
    email: str
    phone: str

    class Config:
        from_attributes = True


class EducationSchema(BaseModel):
    degree: str
    institute: str
    year: str

    class Config:
        from_attributes = True


class ProfessionalSchema(BaseModel):
    company: str
    designation: str
    duration: str

    class Config:
        from_attributes = True