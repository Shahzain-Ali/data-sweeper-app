import streamlit as st
import pandas as pd 
from io import BytesIO
import os

# Set page config must be the first Streamlit command

st.set_page_config(page_title="💿 Data sweeper", layout="wide")

# Load CSS
def load_css():
    with open('styles/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

st.title("💿 Data Sweeper")
st.subheader("By Shahzain Ali")
st.write("Transform your file between CSV and Excel formats with built-in data cleaning and visualization")


uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv","xlsx"],accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file) 
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file extension type: {file_ext}")
            continue

        # Display info about the file 

        st.write(f"File Name: {file.name}")
        st.write(f"File Size: {file.size}")

        # Display first 5 rows of dataframe

        st.write(df.head())


        # Options for cleaning data
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1,col2 = st.columns(2)

            with col1:
                if st.button(f"Remove duplicate from {file.name}"):
                    df.drop_duplicates(inplace=True) #  inplace=True means modifying the original DataFrame without needing to store it in a new variable.
                    st.write("Duplicates Removed!")
            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns #Sirf numbers wale columns par kaam hoga, text (string) wale columns par nahi.
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing values have been filled!")

        # Choose specific column to keep or convert 
        st.subheader("Select columns to convert")
        columns = st.multiselect(f"Choose columns for {file.name}", df.columns , default=df.columns)
        df = df[columns]


        # Create some visualizations
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include=['number']).iloc[:,:2])
            #All rows will remain (: means all rows), but only the first two columns will be kept (:2 means the first two).

        
        # Conversion Options 
        st.subheader(f"Conversion options")
        conversion_type = st.radio(f"Convert {file.name} to:",["csv","excel"],key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "csv":
                df.to_csv(buffer,index=False)
                file_name = file.name.replace(file_ext,".csv")
                mime_type = "text/csv"

            elif conversion_type == "excel":
                df.to_excel(buffer,index=False)
                file_name = file.name.replace(file_ext,".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                #"vnd.openxmlformats-officedocument.spreadsheetml.sheet" → Yeh batata hai ke yeh Excel (.xlsx)
            buffer.seek(0) #buffer.seek(0) yeh cursor ko start (0th position) par le aata hai.

            # Download Button 
            st.download_button(
                label=f"🔽Download {file.name} as {conversion_type}",
                data=buffer.getvalue(),  # ✔️ File ka data read karne ke liye
                file_name=file_name,  # ✔️ `filename` ko `file_name` likhna hoga
                mime=mime_type
            )

st.success("✅All files successfully processed!")