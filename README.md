# Resume Parser API

A FastAPI-based application that parses resume files, extracts key information such as personal details, education, and professional experience, and stores the data in a SQLite database using SQLAlchemy.

## Overview

This project provides a simple REST API for uploading resumes and extracting structured information from them. It is useful for recruitment systems, applicant tracking, and resume management workflows.

## Features

- Upload resume files in supported formats
- Extract personal details such as name, email, and phone number
- Extract education details
- Extract professional experience details
- Validate email and mobile number format
- Prevent duplicate person entries using email or mobile number
- Store parsed data in SQLAlchemy models
- Retrieve and delete saved records through REST APIs

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite

## Project Structure

```bash
resume_parsor_db/
│
├── app.py
├── database.py
├── models.py
├── schemas.py
├── requirements.txt
├── resumes/
├── utils/
│   └── parser.py
└── tests/
```

## Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd resume_parsor_db
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

The application will be available at:

```bash
http://127.0.0.1:8000
```

## API Endpoints

### Person Details

- POST /personDetails
- GET /personDetails
- GET /personDetails/{id}
- DELETE /personDetails/{id}
- DELETE /personDetails

### Education Details

- POST /educationDetails
- GET /educationDetails
- GET /educationDetails/{id}
- DELETE /educationDetails/{id}
- DELETE /educationDetails

### Professional Details

- POST /professionalDetails
- GET /professionalDetails
- GET /professionalDetails/{id}
- DELETE /professionalDetails/{id}
- DELETE /professionalDetails

## Database

The application uses SQLite with SQLAlchemy ORM. The following tables are created automatically:

- person_details
- education_details
- professional_details

## Validation Rules

- Email must be in a valid format
- Mobile number must contain exactly 10 digits
- Duplicate person uploads are rejected if the email or mobile number already exists

## Example Usage

Upload a resume using the person details endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/personDetails" -F "file=@resume.pdf"
```

## Future Enhancements

- Improve resume parsing accuracy
- Support more file formats
- Add authentication and authorization
- Integrate with a cloud database
- Add advanced resume matching and search features

## License

This project is for educational and demonstration purposes.
