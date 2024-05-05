import streamlit as st
import PyPDF2
import re
import pandas as pd
import os
import tempfile
import base64

def extract_transactions_from_pdf(pdf_file_path):
    transactions = []
    
    with open(pdf_file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            
            # Define patterns for extracting different fields
            date_pattern = r'[A-Z][a-z]{2} \d{1,2}, \d{4}' # Match date in format "Apr 28, 2024"
            type_pattern = r'(DEBIT|CREDIT)'
            time_pattern = r'(\d{2}:\d{2} (?:AM|PM))' 
            amount_pattern = r'₹\d+(?:,\d+)*\.?\d+'
            description_pattern = r'(?:AM|PM)\n([\s\S]*?)(?=\nTransaction ID)'
            
            # Extract data using regex patterns
            dates = re.findall(date_pattern, text)
            types = re.findall(type_pattern, text)
            times = re.findall(time_pattern, text)
            amounts = re.findall(amount_pattern, text)
            descriptions = re.findall(description_pattern, text)
            
            cleaned_descriptions = []
            for transaction in descriptions:
                # Split the string into parts based on '\n' separator
                parts = transaction.split('\n')
                details = parts[2].strip()
                # Append the cleaned transaction to the list
                cleaned_descriptions.append(details)
            
            # Combine extracted data into a list of dictionaries
            for date, typ, time, amount, description in zip(dates, types, times, amounts, cleaned_descriptions):
                transaction_data = {
                    "Date": date,
                    "Type": typ,
                    "Time": time,
                    "Amount": amount,
                    "Description": description
                }
                transactions.append(transaction_data)
    
    return transactions

def main():
    st.title("PDF Transaction Extractor")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            transactions = extract_transactions_from_pdf(temp_file.name)

        df = pd.DataFrame(transactions)

        # Convert 'Date' column to datetime format
        df['Date'] = pd.to_datetime(df['Date'], format='%b %d, %Y')
        # Clean 'Amount' column
        df['Amount'] = df['Amount'].str.replace('₹', '').str.replace(',', '').astype(float)

        st.write("Extracted DataFrame:")
        st.write(df)

        # Add a download button for the CSV file
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="transactions.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)

        # Clean up the temporary file
        os.unlink(temp_file.name)

if __name__ == "__main__":
    main()