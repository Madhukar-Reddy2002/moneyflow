import pandas as pd
import plotly.express as px
import streamlit as st

def payee_stats(df):
    # Select payee from sidebar
    selected_payee = st.sidebar.selectbox('Select Payee', df['Payee'].unique())
    
    # Filter transactions for the selected payee
    payee_df = df[df['Payee'] == selected_payee]
    
    # Display the transactions for the selected payee
    st.subheader(f'Transactions for Payee: {selected_payee}')
    st.write(payee_df)
    
    # Insights based on transactions for the selected payee
    st.subheader('Insights based on Transactions')
    
    # Total transactions count
    total_transactions = len(payee_df)
    st.write(f'Total number of transactions: {total_transactions}')
    
    # Total amount spent and received
    total_spent = payee_df[payee_df['Type'] == 'DEBIT']['Amount'].sum()
    total_received = payee_df[payee_df['Type'] == 'CREDIT']['Amount'].sum()
    st.write(f'Total amount spent: {total_spent:.2f}')
    st.write(f'Total amount received: {total_received:.2f}')
    
    # Plot total transactions over time
    st.subheader('Total Transactions Over Time')
    fig1 = px.histogram(payee_df, x='Datetime', nbins=12, title='Total Transactions Over Time')
    st.plotly_chart(fig1, use_container_width=True)
    
    # Plot amount spent vs. amount received over time
    st.subheader('Amount Spent vs. Amount Received Over Time')
    fig2 = px.line(payee_df, x='Datetime', y='Amount', color='Type', title='Amount Spent vs. Amount Received Over Time')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Plot transaction distribution by type
    st.subheader('Transaction Distribution by Type')
    fig3 = px.histogram(payee_df, x='Type', title='Transaction Distribution by Type')
    st.plotly_chart(fig3, use_container_width=True)
    
    # Group transactions by year and type (debit/credit)
    year_grouped = payee_df.groupby([payee_df['Datetime'].dt.year, 'Type'])['Amount'].sum().reset_index()
    
    # Plot yearly credit and debit amounts
    st.subheader('Yearly Credit and Debit Amounts')
    fig4 = px.bar(year_grouped, x='Datetime', y='Amount', color='Type', barmode='group', labels={'Datetime': 'Year', 'Amount': 'Amount'}, title='Yearly Credit and Debit Amounts')
    st.plotly_chart(fig4, use_container_width=True)
    
    # Plot monthly credit and debit amounts
    st.subheader('Monthly Credit and Debit Amounts')
    month_grouped = payee_df.groupby([payee_df['Datetime'].dt.month, 'Type'])['Amount'].sum().reset_index()
    fig5 = px.bar(month_grouped, x='Datetime', y='Amount', color='Type', barmode='group', labels={'Datetime': 'Month', 'Amount': 'Amount'}, title='Monthly Credit and Debit Amounts')
    st.plotly_chart(fig5, use_container_width=True)
    
    # Plot transaction amounts distribution
    st.subheader('Transaction Amounts Distribution')
    fig6 = px.histogram(payee_df, x='Amount', nbins=20, title='Transaction Amounts Distribution')
    st.plotly_chart(fig6, use_container_width=True)