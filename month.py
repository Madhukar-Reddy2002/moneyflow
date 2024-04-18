import streamlit as st

def main(df):
    # Sidebar for user input
    selected_year = st.sidebar.selectbox('Select Year', df['date'].dt.year.unique())
    selected_month = st.sidebar.selectbox('Select Month', df['date'].dt.month_name().unique())

    # Year-wise statistics
    year_df = df[df['date'].dt.year == selected_year]

    # Month-wise statistics
    month_df = year_df[year_df['date'].dt.month_name() == selected_month]
    st.subheader(f'Month-wise Statistics ({selected_month} {selected_year})')
    total_transactions = len(month_df)
    total_amount = month_df['amount'].sum()
    avg_amount = month_df['amount'].mean()
    st.write(f'Total Transactions: {total_transactions}')
    st.write(f'Total Amount Spent: {total_amount:.2f}')
    st.write(f'Average Transaction Amount: {avg_amount:.2f}')

    top_payees = month_df.groupby('payee')['amount'].sum().sort_values(ascending=False).head(5)
    st.write('Top 5 Payees by Amount Spent:')
    st.bar_chart(top_payees)

    daily_amounts = month_df.groupby(month_df['date'].dt.day)['amount'].sum()
    st.write('Daily Transaction Amounts:')
    st.line_chart(daily_amounts)