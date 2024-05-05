import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
from month import main as month_main
from payee import payee_stats
from pavan import process_pdf_file
# Streamlit app
st.title('Money Flow Assistant')

# Sidebar for file upload and analysis type selection
analysis_type = st.sidebar.radio('Select Analysis Type', ['Year-wise', 'Month-wise', 'Payee Wise', 'PDF_to_CSV'])

if analysis_type in ['Year-wise', 'Month-wise', 'Payee Wise']:
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        # Custom function to convert date and time strings to datetime
        def parse_datetime(date_str, time_str):
            datetime_str = f"{date_str} {time_str}"
            return datetime.strptime(datetime_str, "%b %d, %Y %I:%M %p")
        df['Datetime'] = df.apply(lambda row: parse_datetime(row['Date'], row['Time']), axis=1)
        if analysis_type == 'Year-wise':
            # Year-wise analysis
            selected_year = st.sidebar.selectbox('Select Year', df['Datetime'].dt.year.unique())
            year_df = df[df['Datetime'].dt.year == selected_year]
            # Display year-wise statistics
            st.subheader(f'Year-wise Statistics ({selected_year})')
            #Columns for key metrics
            col1, col2, col3 = st.columns((1, 1, 2))  # Adjusting column widths for mobile friendliness

            total_transactions = len(year_df)
            total_amount_spent = year_df[year_df['Type'] == 'DEBIT']['Amount'].sum()
            total_amount_received = year_df[year_df['Type'] == 'CREDIT']['Amount'].sum()
            net_amount = total_amount_received - total_amount_spent

            col1.metric("Total Transactions", f"{total_transactions:,}")
            col2.metric("Total Spent", f"₹{total_amount_spent:,.2f}")
            col3.metric("Total Received", f"₹{total_amount_received:,.2f}")

            # Additional statistics displayed below
            st.write(f'Net Amount: ₹{net_amount:,.2f}')

            # Monthly pie chart
            monthly_amounts = year_df[year_df['Type'] == 'DEBIT'].groupby(year_df['Datetime'].dt.month)['Amount'].sum().reset_index()
            month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            monthly_amounts['month'] = monthly_amounts['Datetime'].apply(lambda x: month_names[x - 1])
            
            st.subheader(f'Monthly Transaction Amounts (Year: {selected_year})')
            st.plotly_chart(px.pie(monthly_amounts, values='Amount', names='month', title='Monthly Spending Distribution'), use_container_width=True)

            # Display highest spending month using a metric
            highest_spending_month = monthly_amounts.loc[monthly_amounts['Amount'].idxmax()]
            st.metric("Highest Spending Month", highest_spending_month['month'], f"₹{highest_spending_month['Amount']}")
            # Bar chart showing top 7 payees according to sum of amount spent
            top_payees = year_df[year_df['Type'] == 'DEBIT'].groupby(['Payee', year_df['Datetime'].dt.month])['Amount'].sum().reset_index().rename(columns={'Datetime': 'month'})
            top_payees['month'] = top_payees['month'].apply(lambda x: month_names[x - 1])
            top_payees = top_payees.groupby('Payee')['Amount'].sum().nlargest(7).reset_index()

            st.subheader('Top 7 Payees by Amount Spent:')
            st.plotly_chart(px.bar(top_payees, x='Payee', y='Amount', title='Top 7 Payees by Amount Spent', labels={'Payee': 'Payee', 'Amount': 'Amount Spent'}), use_container_width=True)

            # Display highest spender and month of highest spending in key points using metrics
            highest_spender = top_payees.loc[top_payees['Amount'].idxmax()]    
            st.metric("Highest Spender", highest_spender['Payee'], f"₹{highest_spender['Amount']}")
            # Bar chart showing top 7 payees according to sum of amount spent
            top_rec = year_df[year_df['Type'] == 'CREDIT'].groupby(['Payee', year_df['Datetime'].dt.month])['Amount'].sum().reset_index().rename(columns={'Datetime': 'month'})
            top_rec['month'] = top_rec['month'].apply(lambda x: month_names[x - 1])
            top_rec = top_rec.groupby('Payee')['Amount'].sum().nlargest(10).reset_index()

            st.subheader('Top 7 Payees by Amount Received:')
            st.plotly_chart(px.bar(top_rec, x='Payee', y='Amount', title='Top 7 Payees by Amount Spent', labels={'Payee': 'Payee', 'Amount': 'Amount Received'}), use_container_width=True)

            # Display highest spender and month of highest spending in key points using metrics
            highest_spender = top_payees.loc[top_payees['Amount'].idxmax()]    
            st.metric("Highest Sender", highest_spender['Payee'], f"₹{highest_spender['Amount']}")

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