import os
import re
from typing import List, Dict

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None

try:
    import docx
except ImportError:  # pragma: no cover
    docx = None

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:  # pragma: no cover
    nlp = None


def read_resume(file_path: str) -> str:
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        if pdfplumber is None:
            return ""
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    if extension == ".docx":
        if docx is None:
            return ""
        document = docx.Document(file_path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    if extension in {".txt", ".md"}:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()

    return ""


def get_personal_details(text: str) -> Dict[str, str]:
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text or "")
    email = email_match.group() if email_match else ""

    phone = ""
    phone_patterns = [
        r"\b(?:phone|mobile|contact(?:\s+no)?|tel(?:ephone)?|mob)\b[^\d+]{0,10}(\+?\d[\d\s-]{7,14}\d)",
        r"(\+?\d[\d\s-]{7,14}\d)",
    ]

    for pattern in phone_patterns:
        phone_match = re.search(pattern, text or "", re.I)
        if phone_match:
            candidate = re.sub(r"\D", "", phone_match.group(1))
            if len(candidate) == 10:
                phone = candidate
            else:
                phone = candidate[-10:] if len(candidate) > 10 else ""
            break

    name = ""

    if nlp is not None:
        for ent in nlp(text or "").ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break

    return {
        "name": name,
        "email": email,
        "phone": phone,
    }


def get_education_details(text: str) -> List[Dict[str, str]]:
    education = []
    degrees = [
        "B.Tech",
        "B.E",
        "BE",
        "BCA",
        "BSc",
        "B.Sc",
        "MCA",
        "M.Tech",
        "MBA",
        "MSc",
        "M.Sc",
        "PhD",
        "MPhil",
        "Diploma",
    ]

    cleaned_text = re.sub(r"\s+", " ", (text or "")).strip()
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]

    for line in lines:
        lower_line = line.lower()
        for degree in degrees:
            if degree.lower() in lower_line:
                education.append({
                    "degree": degree,
                    "institute": line,
                    "year": "",
                })
                break

    if not education:
        for degree in degrees:
            if degree.lower() in cleaned_text.lower():
                education.append({
                    "degree": degree,
                    "institute": cleaned_text,
                    "year": "",
                })
                break

    return education


def get_professional_details(text: str) -> List[Dict[str, str]]:
    experience = []
    cleaned_text = re.sub(r"\s+", " ", (text or "")).strip()
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]

    def normalize_line(line: str) -> str:
        return re.sub(r"^[\-•*\d\.\)\s]+", "", line).strip()

    def extract_date_info(candidate_lines: List[str]) -> tuple[str, str, str]:
        for candidate in candidate_lines:
            month_year_match = re.search(
                r"\b((jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s*\d{4})\s*(?:-|–|to)\s*((present)|((jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s*\d{4})|(\d{4}))\b",
                candidate,
                re.I,
            )
            if month_year_match:
                start_year = re.search(r"(\d{4})", month_year_match.group(1), re.I).group(1)
                end_value = month_year_match.group(3)
                end_year = "Present" if re.search(r"present", end_value, re.I) else re.search(r"(\d{4})", end_value, re.I).group(1)
                return candidate, start_year, end_year

            year_range_match = re.search(r"\b(\d{4})\s*(?:-|–|to)\s*(present|\d{4})\b", candidate, re.I)
            if year_range_match:
                return candidate, year_range_match.group(1), "Present" if re.search(r"present", year_range_match.group(2), re.I) else year_range_match.group(2)

            year_match = re.search(r"\b(\d{4})\b", candidate)
            if year_match:
                return candidate, year_match.group(1), year_match.group(1)

        return "", "", ""

    def extract_technologies(candidate_lines: List[str]) -> str:
        tech_keywords = [
            "python", "java", "sql", "mysql", "postgresql", "mongodb", "redis",
            "django", "flask", "fastapi", "spring", "hibernate", "react", "angular",
            "javascript", "typescript", "html", "css", "aws", "azure", "docker", "kubernetes",
            "git", "linux", "restapi", "api", "pytest", "pandas", "numpy", "spark", "hadoop",
            "tableau", "powerbi", "machine learning", "ai", "selenium", "opencv"
        ]
        found = []
        for candidate in candidate_lines:
            lower = candidate.lower()
            for tech in tech_keywords:
                if tech in lower and tech not in found:
                    found.append(tech)
        return ", ".join(found)

    # Split the resume into work-experience-like sections using common headings.
    sections = []
    current = []
    for line in lines:
        lower = line.lower()
        if any(token in lower for token in ["experience", "work history", "professional experience", "employment", "career", "projects"]):
            if current:
                sections.append(current)
                current = []
            continue
        current.append(line)
    if current:
        sections.append(current)

    if not sections:
        sections = [lines]

    for section in sections:
        for index, line in enumerate(section):
            normalized_line = normalize_line(line)
            lower_line = normalized_line.lower()
            if not normalized_line:
                continue

            context_lines = [normalize_line(item) for item in section[max(0, index - 1):min(len(section), index + 3)]]
            date_line, start_year, end_year = extract_date_info(context_lines)
            duration = date_line

            designation = ""
            for candidate in context_lines:
                lower_candidate = candidate.lower()
                if any(token in lower_candidate for token in ["engineer", "developer", "analyst", "manager", "consultant", "lead", "architect", "intern"]):
                    designation = candidate
                    break

            company = ""
            if re.search(r"@|\.com|\.in|\.org|\.io", normalized_line):
                company = re.sub(r".*?at\s+", "", normalized_line, flags=re.I).strip()
                company = re.sub(r"\b(was|worked|as)\b.*", "", company, flags=re.I).strip()
            elif len(normalized_line.split()) <= 5 and not any(token in lower_line for token in ["experience", "skills", "education", "summary", "projects"]) and not re.search(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|python|java|sql|django|flask|react|javascript|typescript|aws|azure|docker|kubernetes|git|api|rest|html|css|pandas|numpy|spark|hadoop|tableau|powerbi)\b", normalized_line, re.I):
                company = normalized_line

            if company:
                experience.append({
                    "company": company,
                    "designation": designation or "",
                    "start_date": start_year,
                    "end_date": end_year,
                    "duration": duration,
                    "technologies_worked": extract_technologies(context_lines),
                    "other_details": ", ".join([item for item in context_lines if item and item not in {company, designation, duration}]),
                })

    if not experience:
        for line in lines:
            normalized_line = normalize_line(line)
            if not normalized_line:
                continue
            if re.search(r"@|\.com|\.in|\.org|\.io", normalized_line) or len(normalized_line.split()) <= 5:
                experience.append({
                    "company": normalized_line,
                    "designation": "",
                    "start_date": "",
                    "end_date": "",
                    "duration": "",
                    "technologies_worked": "",
                    "other_details": "",
                })

    if not experience:
        for line in lines:
            normalized_line = normalize_line(line)
            if not normalized_line:
                continue
            if re.search(r"@|\.com|\.in|\.org|\.io", normalized_line) or len(normalized_line.split()) <= 5:
                experience.append({
                    "company": normalized_line,
                    "designation": "",
                    "start_date": "",
                    "end_date": "",
                    "duration": "",
                    "technologies_worked": "",
                    "other_details": "",
                })

    return experience
