import streamlit as st
import pandas as pd
from datetime import datetime

# Custom function to convert date and time strings to datetime
def parse_datetime(date_str, time_str):
    datetime_str = f"{date_str} {time_str}"
    return datetime.strptime(datetime_str, "%b %d, %Y %I:%M %p")

# Streamlit app
def main():
    st.title('CSV File Viewer')

    # File upload
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        # Read CSV file into DataFrame
        df = pd.read_csv(uploaded_file)

        # Convert "Date" and "Time" columns to datetime using custom function
        df['Datetime'] = df.apply(lambda row: parse_datetime(row['Date'], row['Time']), axis=1)

        # Display DataFrame head
        st.subheader("Dataset Head")
        st.write(df.head())

if __name__ == "__main__":
    main()