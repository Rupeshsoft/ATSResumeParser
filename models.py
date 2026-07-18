from sqlalchemy import Column, Integer, String
from database import Base

class Person(Base):
    __tablename__ = "person_details"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)


class Education(Base):
    __tablename__ = "education_details"

    id = Column(Integer, primary_key=True)
    degree = Column(String)
    institute = Column(String)
    year = Column(String)


class Professional(Base):
    __tablename__ = "professional_details"

    id = Column(Integer, primary_key=True)
    company = Column(String)
    designation = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    duration = Column(String)
    technologies_worked = Column(String)
    other_details = Column(String)