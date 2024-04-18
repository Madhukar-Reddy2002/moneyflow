import streamlit as st
import pandas as pd
from datetime import datetime
import month

# Load the data
df = pd.read_csv('transactions2.csv')

# Convert date column to datetime format
df['date'] = pd.to_datetime(df['date'])

df = df[df["amount"] <= 900]

# Streamlit app
st.title('Transaction Analysis')

# Sidebar for user input
analysis_type = st.sidebar.radio('Select Analysis Type', ['Year-wise', 'Month-wise'])

if analysis_type == 'Year-wise':
    selected_year = st.sidebar.selectbox('Select Year', df['date'].dt.year.unique())
    # Year-wise statistics
    year_df = df[df['date'].dt.year == selected_year]
    st.subheader(f'Year-wise Statistics ({selected_year})')

    total_transactions = len(year_df)
    total_amount_spent = year_df[year_df['type'] == 'DEBIT']['amount'].sum()
    total_amount_received = year_df[year_df['type'] == 'CREDIT']['amount'].sum()

    st.write(f'Total Transactions: {total_transactions}')
    st.write(f'Total Amount Spent: ${total_amount_spent:.2f}')
    st.write(f'Total Amount Received: ${total_amount_received:.2f}')
    st.write(f'Net Amount: ${total_amount_received - total_amount_spent:.2f}')

    top_payees = year_df.groupby('payee')['amount'].sum().sort_values(ascending=False).head(5)
    st.write('Top 5 Payees by Total Amount Spent:')
    st.bar_chart(top_payees)

    monthly_amounts = year_df.groupby(year_df['date'].dt.month)['amount'].sum()
    st.write('Monthly Transaction Amounts:')
    st.bar_chart(monthly_amounts)

else:
    month.main(df)