import re

import pytesseract

from PIL import Image

from pdf2image import convert_from_path


def extract_text_from_image(image_path):

    image = Image.open(image_path)

    text = pytesseract.image_to_string(image)

    return text


def extract_text_from_pdf(pdf_path):

    pages = convert_from_path(pdf_path)

    full_text = ""

    for page in pages:

        text = pytesseract.image_to_string(page)

        full_text += text

    return full_text


def extract_vehicle_number(text):

    pattern = r'[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}'

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None


def extract_dl_number(text):

    pattern = r'[A-Z]{2}[0-9]{13}'

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None


def extract_student_id(text):

    pattern = r'\b\d{8}\b'

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None


def process_document(document):

    file_path = document.file.path

    if file_path.endswith(".pdf"):

        text = extract_text_from_pdf(
            file_path
        )

    else:

        text = extract_text_from_image(
            file_path
        )

    extracted_data = {
        "vehicle_number": extract_vehicle_number(
            text
        ),
        "dl_number": extract_dl_number(
            text
        ),
        "student_id": extract_student_id(
            text
        ),
        "raw_text": text
    }

    return extracted_data