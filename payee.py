import pandas as pd
import plotly.express as px
import streamlit as st

def payee_stats(df):
    # Select payee from sidebar
    selected_payee = st.sidebar.selectbox('Select Payee', df['payee'].unique())
    
    # Filter transactions for the selected payee
    payee_df = df[df['payee'] == selected_payee]

    # Display the transactions for the selected payee
    st.subheader(f'Transactions for Payee: {selected_payee}')
    st.write(payee_df)

    # Insights based on transactions for the selected payee
    st.subheader('Insights based on Transactions')

    # Plot total transactions over time
    st.subheader('Total Transactions Over Time')
    fig1 = px.histogram(payee_df, x='date', title='Total Transactions Over Time')
    st.plotly_chart(fig1)

    # Plot amount spent vs. amount received over time
    st.subheader('Amount Spent vs. Amount Received Over Time')
    fig2 = px.line(payee_df, x='date', y='amount', color='type', title='Amount Spent vs. Amount Received Over Time')
    st.plotly_chart(fig2)

    # Plot transaction distribution by type
    st.subheader('Transaction Distribution by Type')
    fig3 = px.histogram(payee_df, x='type', title='Transaction Distribution by Type')
    st.plotly_chart(fig3)

    # Group transactions by year and type (debit/credit)
    year_grouped = payee_df.groupby([payee_df['date'].dt.year, 'type'])['amount'].sum().reset_index()

    # Plot yearly credit and debit amounts
    st.subheader('Yearly Credit and Debit Amounts')
    fig4 = px.bar(year_grouped, x='date', y='amount', color='type', barmode='group', 
                  labels={'date': 'Year', 'amount': 'Amount'}, 
                  title='Yearly Credit and Debit Amounts')
    st.plotly_chart(fig4)
