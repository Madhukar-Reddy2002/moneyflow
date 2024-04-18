import streamlit as st
import pandas as pd
import plotly.express as px

def main(df):
    # Sidebar for user input
    selected_year = st.sidebar.selectbox('Select Year', df['date'].dt.year.unique())
    selected_month = st.sidebar.selectbox('Select Month', df['date'].dt.month_name().unique())

    # Year-wise statistics
    year_df = df[df['date'].dt.year == selected_year]

    # Month-wise statistics
    month_df = year_df[year_df['date'].dt.month_name() == selected_month]
    st.subheader(f'Month-wise Statistics ({selected_month} {selected_year})')
    # Total transactions, total amount, and average amount
    total_transactions = len(month_df)
    total_amount_spent = month_df[month_df['type'] == 'DEBIT']['amount'].sum()
    total_amount_received = month_df[month_df['type'] == 'CREDIT']['amount'].sum()
    money_saved = total_amount_received - total_amount_spent
    st.write(f'Total Transactions: {total_transactions}')
    st.write(f'Total Amount Received: ₹ {total_amount_received:.2f}')
    st.write(f'Total Amount Spent: ₹ {total_amount_spent:.2f}')
    st.write(f'Total Amount Saved: ₹ {money_saved:.2f}')

    # # Top 5 payees by amount spent
    # top_payees_spent = month_df[month_df['type'] == 'DEBIT'].groupby('payee')['amount'].sum().nlargest(5)
    # st.write('Top 5 Payees by Amount Spent:')
    # st.bar_chart(top_payees_spent)
    st.plotly_chart(px.pie(month_df[month_df['type'] == 'DEBIT'], values='amount', names='payee', title='Money Spent Distribution'))
    # Pie chart for money received
    st.plotly_chart(px.pie(month_df[month_df['type'] == 'CREDIT'], values='amount', names='payee', title='Money Received Distribution'))

    # Daily transaction amounts
    daily_amounts = month_df.groupby(month_df['date'].dt.day)['amount'].sum()
    st.write('Daily Transaction Amounts:')
    st.line_chart(daily_amounts)