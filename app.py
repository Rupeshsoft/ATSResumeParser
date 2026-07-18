import re

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
import models
from utils import parser
import shutil
import os

#import resume_parser
# from resume_parser import (
#     read_resume,
#     get_personal_details,
#     get_education_details,
#     get_professional_details,
# )

# text = read_resume(filepath)
# person = get_personal_details(text)

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


init_db()

app = FastAPI(
    title="Resume Parser API",
    version="1.0",
    description="Resume Parser using FastAPI"
)

UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def validate_person_data(person_data: dict):
    email = (person_data or {}).get("email", "") or ""
    phone = (person_data or {}).get("phone", "") or ""

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise HTTPException(status_code=422, detail="Invalid email format")

    if not re.fullmatch(r"\d{10}", phone):
        raise HTTPException(status_code=422, detail="Mobile no must be 10 digit numbers only")

    return person_data


def find_existing_person(db: Session, person_data: dict):
    email = (person_data or {}).get("email", "")
    phone = (person_data or {}).get("phone", "")

    if email and phone:
        return db.query(models.Person).filter(
            or_(models.Person.email == email, models.Person.phone == phone)
        ).first()

    if email:
        return db.query(models.Person).filter(models.Person.email == email).first()

    if phone:
        return db.query(models.Person).filter(models.Person.phone == phone).first()

    return None


def save_resume_data(file_path: str, db: Session):
    text = parser.read_resume(file_path)

    person = parser.get_personal_details(text)
    validate_person_data(person)

    existing = find_existing_person(db, person)
    if existing:
        raise HTTPException(status_code=409, detail="Duplicate Email or Mobile no")

    person_obj = models.Person(**person)
    db.add(person_obj)
    db.flush()

    education_data = parser.get_education_details(text)
    education_objs = []
    for edu in education_data:
        edu_obj = models.Education(**edu)
        db.add(edu_obj)
        education_objs.append(edu_obj)

    professional_data = parser.get_professional_details(text)
    professional_objs = []
    for exp in professional_data:
        pro_obj = models.Professional(**exp)
        db.add(pro_obj)
        professional_objs.append(pro_obj)

    db.commit()

    return {
        "person": person_obj,
        "education": education_objs,
        "professional": professional_objs,
    }


# --------------------------
# PERSON DETAILS
# --------------------------

@app.post(
    "/personDetails",
    tags=["Person"],
    summary="Upload Resume and Extract Personal Details"
)
def save_person(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = save_resume_data(filepath, db)

        return result["person"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/personDetails",
    tags=["Person"],
    summary="Get All Person Details"
)
def list_persons(db: Session = Depends(get_db)):
    return db.query(models.Person).all()


@app.get(
    "/personDetails/{id}",
    tags=["Person"],
    summary="Get Person by ID"
)
def get_person(id: int, db: Session = Depends(get_db)):

    person = db.query(models.Person).filter(models.Person.id == id).first()

    if not person:
        raise HTTPException(status_code=404, detail="Person Not Found")

    return person


@app.delete(
    "/personDetails/{id}",
    tags=["Person"],
    summary="Delete Person by ID"
)
def delete_person(id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter(models.Person.id == id).first()

    if not person:
        raise HTTPException(status_code=404, detail="Person Not Found")

    db.delete(person)
    db.commit()
    return {"message": "Person deleted successfully"}


@app.delete(
    "/personDetails",
    tags=["Person"],
    summary="Delete All Person Details"
)
def delete_all_persons(db: Session = Depends(get_db)):
    db.query(models.Person).delete()
    db.commit()
    return {"message": "All person details deleted successfully"}


# --------------------------
# EDUCATION
# --------------------------

@app.post(
    "/educationDetails",
    tags=["Education"],
    summary="Upload Resume and Save Education"
)
def education(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = parser.read_resume(filepath)

    data = parser.get_education_details(text)

    saved = []

    for edu in data:

        obj = models.Education(**edu)

        db.add(obj)

        db.commit()

        db.refresh(obj)

        saved.append(obj)

    return {
        "message": "Education details saved successfully",
        "data": saved,
    }


@app.get(
    "/educationDetails",
    tags=["Education"],
    summary="Get All Education Details"
)
def list_education(db: Session = Depends(get_db)):
    return db.query(models.Education).all()


@app.get(
    "/educationDetails/{id}",
    tags=["Education"],
    summary="Get Education by ID"
)
def get_education(id: int, db: Session = Depends(get_db)):

    edu = db.query(models.Education).filter(models.Education.id == id).first()

    if not edu:
        raise HTTPException(status_code=404, detail="Education Not Found")

    return edu


@app.delete(
    "/educationDetails/{id}",
    tags=["Education"],
    summary="Delete Education by ID"
)
def delete_education(id: int, db: Session = Depends(get_db)):
    edu = db.query(models.Education).filter(models.Education.id == id).first()

    if not edu:
        raise HTTPException(status_code=404, detail="Education Not Found")

    db.delete(edu)
    db.commit()
    return {"message": "Education deleted successfully"}


@app.delete(
    "/educationDetails",
    tags=["Education"],
    summary="Delete All Education Details"
)
def delete_all_education(db: Session = Depends(get_db)):
    db.query(models.Education).delete()
    db.commit()
    return {"message": "All education details deleted successfully"}


# --------------------------
# PROFESSIONAL DETAILS
# --------------------------

@app.post(
    "/professionalDetails",
    tags=["Professional"],
    summary="Upload Resume and Save Professional Details"
)
def professional(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = parser.read_resume(filepath)

    data = parser.get_professional_details(text)

    saved = []

    for exp in data:

        obj = models.Professional(**exp)

        db.add(obj)

        db.commit()

        db.refresh(obj)

        saved.append(obj)

    return {
        "message": "Professional details saved successfully",
        "data": saved,
    }


@app.get(
    "/professionalDetails",
    tags=["Professional"],
    summary="Get All Professional Details"
)
def list_professional(db: Session = Depends(get_db)):
    return db.query(models.Professional).all()


@app.get(
    "/professionalDetails/{id}",
    tags=["Professional"],
    summary="Get Professional Details by ID"
)
def get_professional(id: int, db: Session = Depends(get_db)):

    pro = db.query(models.Professional).filter(models.Professional.id == id).first()

    if not pro:
        raise HTTPException(status_code=404, detail="Professional Details Not Found")

    return pro


@app.delete(
    "/professionalDetails/{id}",
    tags=["Professional"],
    summary="Delete Professional Details by ID"
)
def delete_professional(id: int, db: Session = Depends(get_db)):
    pro = db.query(models.Professional).filter(models.Professional.id == id).first()

    if not pro:
        raise HTTPException(status_code=404, detail="Professional Details Not Found")

    db.delete(pro)
    db.commit()
    return {"message": "Professional details deleted successfully"}


@app.delete(
    "/professionalDetails",
    tags=["Professional"],
    summary="Delete All Professional Details"
)
def delete_all_professional(db: Session = Depends(get_db)):
    db.query(models.Professional).delete()
    db.commit()
    return {"message": "All professional details deleted successfully"}