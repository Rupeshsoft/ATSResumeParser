import os
import tempfile
import unittest

from fastapi import HTTPException

from utils import parser
from app import find_existing_person, save_resume_data, validate_person_data
from database import Base, SessionLocal
import models


class ParserPhoneTest(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        Base.metadata.drop_all(bind=self.db.get_bind())
        Base.metadata.create_all(bind=self.db.get_bind())

    def tearDown(self):
        self.db.close()

    def test_duplicate_person_is_detected_by_email_or_phone(self):
        self.db.add(models.Person(name="John", email="john@example.com", phone="9876543210"))
        self.db.commit()

        existing = find_existing_person(self.db, {"email": "john@example.com", "phone": "9999999999"})
        self.assertIsNotNone(existing)

        existing_by_phone = find_existing_person(self.db, {"email": "", "phone": "9876543210"})
        self.assertIsNotNone(existing_by_phone)

    def test_extracts_phone_with_label_and_country_code(self):
        text = "John Doe\nEmail: john@example.com\nPhone No: +91 9876543210"
        details = parser.get_personal_details(text)
        self.assertEqual(details["phone"], "9876543210")

    def test_extracts_phone_with_space_separated_digits(self):
        text = "Jane Smith\nMobile: 98765 43210"
        details = parser.get_personal_details(text)
        self.assertEqual(details["phone"], "9876543210")

    def test_extracts_plain_ten_digit_phone(self):
        text = "Alex Kumar\nContact: 9876543210"
        details = parser.get_personal_details(text)
        self.assertEqual(details["phone"], "9876543210")

    def test_validate_person_data_rejects_invalid_email(self):
        with self.assertRaises(HTTPException):
            validate_person_data({"name": "John", "email": "invalid-email", "phone": "9876543210"})

    def test_validate_person_data_rejects_invalid_phone(self):
        with self.assertRaises(HTTPException):
            validate_person_data({"name": "John", "email": "john@example.com", "phone": "12345"})

    def test_save_resume_data_persists_person_education_and_professional(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as handle:
            handle.write(
                "John Doe\n"
                "Email: john@example.com\n"
                "Phone: 9876543210\n"
                "Education: B.Tech Computer Science\n"
                "Institute: ABC University\n"
                "Experience: Software Engineer at ABC Corp from Jan 2020 to Present"
            )
            path = handle.name

        try:
            result = save_resume_data(path, self.db)
            self.assertEqual(result["person"].email, "john@example.com")
            self.assertGreaterEqual(len(result["education"]), 1)
            self.assertGreaterEqual(len(result["professional"]), 1)
            self.assertEqual(self.db.query(models.Person).count(), 1)
            self.assertGreaterEqual(self.db.query(models.Education).count(), 1)
            self.assertGreaterEqual(self.db.query(models.Professional).count(), 1)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
