import streamlit as st
import pandas as pd
import plotly.express as px
import month

# Load the data
df = pd.read_csv('transactions2.csv')

# Convert date column to datetime format
df['date'] = pd.to_datetime(df['date'])

# Streamlit app
st.title('Money Flow Assistant')

# Sidebar for user input
analysis_type = st.sidebar.radio('Select Analysis Type', ['Year-wise', 'Month-wise'])

if analysis_type == 'Year-wise':
    selected_year = st.sidebar.selectbox('Select Year', df['date'].dt.year.unique())
    # Year-wise statistics
    year_df = df[df['date'].dt.year == selected_year]
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
else:
    month.main(df)
