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

uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv","xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        try:
            if file_ext == ".csv":
                df = pd.read_csv(file) 
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file extension type: {file_ext}")
                continue

            # Display info about the file 
            st.write(f"File Name: {file.name}")
            st.write(f"File Size: {file.size} bytes")

            # Display first 5 rows of dataframe
            st.write(df.head())

            # Options for cleaning data
            st.subheader("Data Cleaning Options")
            if st.checkbox(f"Clean data for {file.name}"):
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Remove duplicate from {file.name}"):
                        initial_rows = len(df)
                        df.drop_duplicates(inplace=True)
                        removed_rows = initial_rows - len(df)
                        st.write(f"Duplicates Removed! ({removed_rows} rows removed)")

                with col2:
                    if st.button(f"Fill Missing Values for {file.name}"):
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        missing_counts = df[numeric_cols].isna().sum()
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.write(f"Missing values filled in {len(numeric_cols)} numeric columns!")
                        if len(missing_counts[missing_counts > 0]) > 0:
                            st.write("Filled missing values per column:", missing_counts[missing_counts > 0])

            # Choose specific columns to keep or convert - FIXED VERSION
            st.subheader("Select columns to convert")
            # Convert column names to a list and create unique key for the widget
            column_options = df.columns.tolist()
            widget_key = f"multiselect_{file.name}"  # Create unique key for each file
            
            # Initialize session state for this widget if it doesn't exist
            if widget_key not in st.session_state:
                st.session_state[widget_key] = column_options
            
            # Create the multiselect with session state
            selected_columns = st.multiselect(
                f"Choose columns for {file.name}",
                options=column_options,
                default=st.session_state[widget_key],
                key=widget_key
            )
            
            if selected_columns:  # Only proceed if columns are selected
                df = df[selected_columns]

                # Create some visualizations
                st.subheader("📊 Data Visualization")
                if st.checkbox(f"Show visualization for {file.name}"):
                    numeric_df = df.select_dtypes(include=['number'])
                    if not numeric_df.empty:
                        st.bar_chart(numeric_df.iloc[:,:2])
                    else:
                        st.warning("No numeric columns available for visualization")

                # Conversion Options 
                st.subheader(f"Conversion options")
                conversion_type = st.radio(f"Convert {file.name} to:", ["csv", "excel"], key=file.name)
                
                if st.button(f"Convert {file.name}"):
                    buffer = BytesIO()
                    if conversion_type == "csv":
                        df.to_csv(buffer, index=False)
                        file_name = file.name.replace(file_ext, ".csv")
                        mime_type = "text/csv"
                    else:  # excel
                        df.to_excel(buffer, index=False)
                        file_name = file.name.replace(file_ext, ".xlsx")
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    
                    buffer.seek(0)

                    # Download Button 
                    st.download_button(
                        label=f"🔽Download {file.name} as {conversion_type}",
                        data=buffer.getvalue(),
                        file_name=file_name,
                        mime=mime_type
                    )
            else:
                st.warning("Please select at least one column to proceed")

        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
            continue

st.success("✅ All files successfully processed!")