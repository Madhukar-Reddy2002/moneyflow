import PyPDF2
import re
import pandas as pd
import tempfile
from datetime import datetime

# Function to extract text from PDF
def extract_text_pypdf2(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        page_text = page.extract_text()
        clean_text = re.sub(r'[^\x00-\x7F]+', '', page_text)
        text += clean_text
    return text

# Custom function to convert date and time strings to datetime
def parse_datetime(date_str, time_str):
    datetime_str = f"{date_str} {time_str}"
    return datetime.strptime(datetime_str, "%b %d, %Y %I:%M %p")

# Function to process text extracted from PDF
def extract_transactions(text):
    combined_text = text.replace('\n', ' ')
    pattern = r"(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b.*?)(?=Transaction\sID)"
    start = combined_text.find("Amount")
    matches = re.findall(pattern, combined_text[start:])

    data = []
    pattern = r"(\w{3}\s\d{2},\s\d{4})\s(\d{2}:\d{2}\s[AP]M)\s(DEBIT|CREDIT)\s(\d+)\s(.*)"

    for transaction in matches:
        match = re.match(pattern, transaction)
        if match:
            date, time, type_, amount, payee = match.groups()
            data.append({
                "Date": date,
                "Time": time,
                "Type": type_,
                "Amount": int(amount),
                "Payee": payee
            })

    df = pd.DataFrame(data)
    return df

# Function to handle PDF file upload and processing
def process_pdf_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file.seek(0)
        text = extract_text_pypdf2(open(temp_file.name, 'rb'))

    df = extract_transactions(text)
    return df