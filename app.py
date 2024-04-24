import streamlit as st
import pandas as pd
import plotly.express as px
import PyPDF2
import re
import os
import tempfile
from datetime import datetime
import base64
from month import main as month_main
from payee import payee_stats

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        all_page_text = []
        for page_num in range(num_pages):
            # Get the page
            page = pdf_reader.pages[page_num]
            
            # Extract text from the page
            page_text = page.extract_text()
            clean_text = re.sub(r'[^\x00-\x7F]+', '', page_text)
            
            # Append the text to the list
            all_page_text.append(clean_text)
            
        return all_page_text

# Function to process text extracted from PDF
def process_transactions_text(all_text):
    pages = []
    for i in all_text:
        li = i.split('\n')
        li2 = li[1::2]
        pages.append(li2)

    transactions_text = []
    pattern = r"(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b.*?)(?=Transaction\sID)"
    for page in pages:
        page_text = " ".join(page)
        matches = re.findall(pattern, page_text)
        transactions_text.append(matches)

    text = transactions_text[0][0]
    text = text.split(" ")
    start = text.index("Amount")
    text = " ".join(text[start+1:])
    transactions_text[0][0] = text

    transactions_nice = []
    for transaction_page in transactions_text:
        for transaction in transaction_page:
            # Split the transaction string by spaces and strip each substring
            stripped_transaction = transaction.split(" ")
            cleared_transaction = [substr.strip() for substr in stripped_transaction if substr.strip()]
            
            # Process each cleared transaction
            month = cleared_transaction[0]
            date = cleared_transaction[1].rstrip(',')
            year = cleared_transaction[2]
            time = cleared_transaction[3] + " " + cleared_transaction[4]
            transaction_date = datetime.strptime(f"{month} {date} {year} {time}", "%b %d %Y %I:%M %p")

            data = {
                "date": transaction_date,
                "type": cleared_transaction[5],
                "amount": cleared_transaction[6],
                "payee": " ".join(cleared_transaction[9:])
            }
            transactions_nice.append(data)

    return transactions_nice

# Function to handle PDF file upload and processing
@st.cache_data()
def process_pdf_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file.seek(0)
        all_text = extract_text_from_pdf(temp_file.name)

    transactions_nice = process_transactions_text(all_text)
    df = pd.DataFrame(transactions_nice)
    return df

# Streamlit app
st.title('Money Flow Assistant')

# Sidebar for file upload and analysis type selection
analysis_type = st.sidebar.radio('Select Analysis Type', ['Year-wise', 'Month-wise', 'Payee Wise', 'PDF_to_CSV'])

if analysis_type in ['Year-wise', 'Month-wise', 'Payee Wise']:
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        # Convert date column to datetime format
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = df['amount'].str.replace(',', '').astype(float)

        if analysis_type == 'Year-wise':
            # Year-wise analysis
            selected_year = st.sidebar.selectbox('Select Year', df['date'].dt.year.unique())
            year_df = df[df['date'].dt.year == selected_year]
            # Display year-wise statistics
            st.subheader(f'Year-wise Statistics ({selected_year})')
            # Columns for key metrics
            col1, col2, col3 = st.columns((1, 1, 2))  # Adjusting column widths for mobile friendliness

            total_transactions = len(year_df)
            total_amount_spent = year_df[year_df['type'] == 'DEBIT']['amount'].sum()
            total_amount_received = year_df[year_df['type'] == 'CREDIT']['amount'].sum()
            net_amount = total_amount_received - total_amount_spent

            col1.metric("Total Transactions", f"{total_transactions:,}")
            col2.metric("Total Spent", f"₹{total_amount_spent:,.2f}")
            col3.metric("Total Received", f"₹{total_amount_received:,.2f}")

            # Additional statistics displayed below
            st.write(f'Net Amount: ₹{net_amount:,.2f}')

            # Monthly pie chart
            monthly_amounts = year_df[year_df['type'] == 'DEBIT'].groupby(year_df['date'].dt.month)['amount'].sum().reset_index()
            month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            monthly_amounts['month'] = monthly_amounts['date'].apply(lambda x: month_names[x - 1])
            
            st.subheader(f'Monthly Transaction Amounts (Year: {selected_year})')
            st.plotly_chart(px.pie(monthly_amounts, values='amount', names='month', title='Monthly Spending Distribution'), use_container_width=True)

            # Display highest spending month using a metric
            highest_spending_month = monthly_amounts.loc[monthly_amounts['amount'].idxmax()]
            st.metric("Highest Spending Month", highest_spending_month['month'], f"₹{highest_spending_month['amount']}")
            # Bar chart showing top 7 payees according to sum of amount spent
            top_payees = year_df[year_df['type'] == 'DEBIT'].groupby(['payee', year_df['date'].dt.month])['amount'].sum().reset_index().rename(columns={'date': 'month'})
            top_payees['month'] = top_payees['month'].apply(lambda x: month_names[x - 1])
            top_payees = top_payees.groupby('payee')['amount'].sum().nlargest(7).reset_index()

            st.subheader('Top 7 Payees by Amount Spent:')
            st.plotly_chart(px.bar(top_payees, x='payee', y='amount', title='Top 7 Payees by Amount Spent', labels={'payee': 'Payee', 'amount': 'Amount Spent'}), use_container_width=True)

            # Display highest spender and month of highest spending in key points using metrics
            highest_spender = top_payees.loc[top_payees['amount'].idxmax()]    
            st.metric("Highest Spender", highest_spender['payee'], f"₹{highest_spender['amount']}")
            # Bar chart showing top 7 payees according to sum of amount spent
            top_rec = year_df[year_df['type'] == 'CREDIT'].groupby(['payee', year_df['date'].dt.month])['amount'].sum().reset_index().rename(columns={'date': 'month'})
            top_rec['month'] = top_rec['month'].apply(lambda x: month_names[x - 1])
            top_rec = top_rec.groupby('payee')['amount'].sum().nlargest(10).reset_index()

            st.subheader('Top 7 Payees by Amount Received:')
            st.plotly_chart(px.bar(top_rec, x='payee', y='amount', title='Top 7 Payees by Amount Spent', labels={'payee': 'Payee', 'amount': 'Amount Received'}), use_container_width=True)

            # Display highest spender and month of highest spending in key points using metrics
            highest_spender = top_payees.loc[top_payees['amount'].idxmax()]    
            st.metric("Highest Sender", highest_spender['payee'], f"₹{highest_spender['amount']}")

        elif analysis_type == 'Month-wise':
            # Month-wise analysis
            st.subheader('Month-wise Analysis')
            month_main(df)
            # Your month-wise analysis code here...

        elif analysis_type == 'Payee Wise':
            # Payee-wise analysis
            st.subheader('Payee-wise Analysis')
            payee_stats(df)
            # Your payee-wise analysis code here...

    else:
        st.warning('Please upload a CSV file to proceed.')

elif analysis_type == 'PDF_to_CSV':
    uploaded_pdf = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_pdf is not None:
        # Process PDF file
        df = process_pdf_file(uploaded_pdf)
        st.write("Extracted DataFrame:")
        st.write(df)

        # Add a download button for the CSV file
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="transactions.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.warning('Please upload a PDF file to proceed.')

else:
    st.warning('Please select an analysis type to proceed.')