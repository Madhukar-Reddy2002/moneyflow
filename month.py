import streamlit as st
import pandas as pd
import plotly.express as px

def main(df):
    # Sidebar for user input
    selected_year = st.sidebar.selectbox('Select Year', df['Datetime'].dt.year.unique())
    selected_month = st.sidebar.selectbox('Select Month', df['Datetime'].dt.month_name().unique())

    # Year-wise statistics
    year_df = df[df['Datetime'].dt.year == selected_year]

    # Month-wise statistics
    month_df = year_df[year_df['Datetime'].dt.month_name() == selected_month]
    st.subheader(f'Month-wise Statistics ({selected_month} {selected_year})')
    # Total transactions, total amount, and average amount
    total_transactions = len(month_df)
    total_amount_spent = month_df[month_df['Type'] == 'DEBIT']['Amount'].sum()
    total_amount_received = month_df[month_df['Type'] == 'CREDIT']['Amount'].sum()
    money_saved = total_amount_received - total_amount_spent
    st.write(f'Total Transactions: {total_transactions}')
    st.write(f'Total Amount Received: ₹ {total_amount_received:.2f}')
    st.write(f'Total Amount Spent: ₹ {total_amount_spent:.2f}')
    st.write(f'Total Amount Saved: ₹ {money_saved:.2f}')

    # # Top 5 payees by amount spent
    # top_payees_spent = month_df[month_df['Type'] == 'DEBIT'].groupby('Payee')['Amount'].sum().nlargest(5)
    # st.write('Top 5 Payees by Amount Spent:')
    # st.bar_chart(top_payees_spent)
    st.plotly_chart(px.pie(month_df[month_df['Type'] == 'DEBIT'], values='Amount', names='Payee', title='Money Spent Distribution'), use_container_width=True)
    # Pie chart for money received
    st.plotly_chart(px.pie(month_df[month_df['Type'] == 'CREDIT'], values='Amount', names='Payee', title='Money Received Distribution'), use_container_width=True)

    # Daily transaction amounts
    daily_amounts = month_df.groupby(month_df['Datetime'].dt.day)['Amount'].sum()
    st.write('Daily Transaction Amounts:')
    st.line_chart(daily_amounts, use_container_width=True)