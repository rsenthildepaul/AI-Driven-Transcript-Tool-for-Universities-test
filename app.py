import re
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os, time
from io import BytesIO
from dotenv import load_dotenv
import pandas as pd



def page_setup():
    st.set_page_config(page_title="Multimedia AI Assistant", layout="wide")
    st.header("Upload transcript (PDF, Images)!")
    st.markdown("<style>#MainMenu {visibility: hidden;}</style>", unsafe_allow_html=True)

def load_universities(file_path):
    """Loads university details from an Excel file."""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            st.sidebar.error(f"File not found: {file_path}")
            return {}

        # Read Excel file
        df = pd.read_excel(file_path)

        # Check if required columns exist
        required_columns = ["Org ID", "Descr", "City", "State"]
        if not all(col in df.columns for col in required_columns):
            st.sidebar.error(f"One or more required columns missing: {required_columns}")
            return {}

        # Create a dictionary of university details
        university_dict = {}
        for _, row in df.iterrows():
            university_dict[row["Descr"]] = {
                "Org ID": row["Org ID"],
                "City": row["City"],
                "State": row["State"],
            }

        return university_dict

    except Exception as e:
        st.sidebar.error(f"Error loading university data: {e}")
        return {}

def get_typeof_media():
    st.sidebar.header("Select Media Type")
    return st.sidebar.radio(
        "Choose one:",
        ("PDF Files", "Images"),
        help="Select the type of file you want to interact with.",
    )

def get_llm_config():
    st.sidebar.header("LLM Configuration")
    model = st.sidebar.radio(
        "Choose Model:",
        ("gemini-2.0-flash", "gemini-2.0-pro"),
        help="Select the LLM model for processing.",
    )
    temperature = st.sidebar.slider(
        "Temperature:",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="Lower values produce more deterministic responses.",
    )
    top_p = st.sidebar.slider(
        "Top P:",
        min_value=0.0,
        max_value=1.0,
        value=0.9,
        step=0.05,
        help="Used for nucleus sampling. Lower values produce less random results.",
    )
    max_tokens = st.sidebar.slider(
        "Max Tokens:",
        min_value=100,
        max_value=5000,
        value=2000,
        step=100,
        help="Maximum number of response tokens.",
    )
    return model, temperature, top_p, max_tokens

def redact_sensitive_info(text):
    """Redacts SSN (following 'SSN') and 10 characters after 'XXX' (case insensitive)."""
    
    # Redact 15 characters after "SSN"
    ssn_pattern = r"(?i)(SSN[:\s]*.{0,15})"
    text = re.sub(ssn_pattern, "SSN [REDACTED]", text)

    # Redact 10 characters after "XXX"
    xxx_pattern = r"(?i)(XXX[:\s]*.{0,10})"
    text = re.sub(xxx_pattern, "XXX [REDACTED]", text)

    return text

def process_pdf(pdf_file):
    """Extracts and processes text from a PDF file, redacting sensitive information."""
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"

    # Apply both SSN & XXX-based redaction
    redacted_text = redact_sensitive_info(text)

    return redacted_text

def upload_and_generate(model, config, content, prompt):
    gen_model = genai.GenerativeModel(model_name=model, generation_config=config)
    response = gen_model.generate_content([content, prompt])
    return response.text

def handle_image_or_file_upload(file_name, model, generation_config):
    """Handles upload for images and video."""
    file = genai.upload_file(path=file_name)
    while file.state.name == "PROCESSING":
        time.sleep(5)
        file = genai.get_file(file.name)
    if file.state.name == "FAILED":
        raise ValueError(f"File processing failed: {file_name}")

    return file

def main():
    load_dotenv()
    page_setup()

    # Load University List from Excel File
    university_file = "/Users/rakulsk/Documents/python/gemini_chatbot-main/EXT_ORG_IDs.xlsx"  # Update if needed
    university_data = load_universities(university_file)

    # Sidebar: Move University Selection to the Top
    st.sidebar.header("Select University")
    if university_data:
        university_names = list(university_data.keys())
        selected_university = st.sidebar.selectbox("Choose your university:", university_names)

        # Retrieve selected university details
        university_details = university_data.get(selected_university, {})

        # Display University Details
        st.sidebar.write(f"**Selected:** {selected_university}")
        st.sidebar.write(f"**Org ID:** {university_details.get('Org ID', 'N/A')}")
        st.sidebar.write(f"**City:** {university_details.get('City', 'N/A')}")
        st.sidebar.write(f"**State:** {university_details.get('State', 'N/A')}")
    else:
        st.sidebar.warning("No universities found. Please check the uploaded file.")
        selected_university = "Unknown University"

    # Move Media Selection Below University Selection
    media_type = get_typeof_media()

    # Move LLM Configuration Below Media Selection
    model, temperature, top_p, max_tokens = get_llm_config()

    config = {
        "temperature": temperature,
        "top_p": top_p,
        "max_output_tokens": max_tokens,
    }

    # Define default and special prompts
    default_prompt = "Extract all rows from the PDF in the format: Year | Term | Subject| Code | Title | Units | Grade and only those columns. Ensure the data is detailed, complete, and structured as a table. Do not add any explanation"
    waubonsee_prompt = "Extract all rows from the PDF in the format: Year | Term | Subject| Code (ex: 102.981=102) | Title | Units | Grade and only those columns. Ensure the data is detailed, complete, and structured as a table. Do not add any explanation"

    # Determine which prompt to use
    extraction_prompt = waubonsee_prompt if selected_university == "Waubonsee Community College" else default_prompt

    if media_type == "PDF Files":
        uploaded_files = st.file_uploader("Upload one or more PDF files", type="pdf", accept_multiple_files=True)
        if uploaded_files:
            combined_text = ""
            for file in uploaded_files:
                # Process the transcript and redact sensitive information
                redacted_text = process_pdf(file)
                combined_text += redacted_text

            st.markdown("### Select a question or enter your own:")
            selected_prompt = st.selectbox("Choose a predefined question:", [extraction_prompt])
            custom_prompt = st.text_input("Or enter your own question:")
            question = custom_prompt if custom_prompt else selected_prompt

            if question:
                # Include selected university in the prompt
                final_prompt = f"University: {selected_university}\nOrg ID: {university_details.get('Org ID', 'N/A')}\nCity: {university_details.get('City', 'N/A')}\nState: {university_details.get('State', 'N/A')}\nPrompt: {question}"
                response_text = upload_and_generate(model, config, combined_text, final_prompt)

                st.markdown("### Response:")
                st.write(response_text)

                # ✅ Add CSV Download Functionality
                try:
                    response_df = pd.read_csv(BytesIO(response_text.encode('utf-8')), sep="|")
                    response_df = response_df.loc[:, ~response_df.columns.str.contains('^Unnamed')]
                    response_df = response_df[~response_df.apply(lambda row: row.astype(str).str.contains("---").any(), axis=1)]
                    
                    csv_response_data = response_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download as CSV",
                        data=csv_response_data,
                        file_name="extracted_data.csv",
                        mime="text/csv",
                    )
                except Exception as e:
                    st.warning("The response could not be converted to CSV. Please ensure it is tabular data.")

            # ✅ Add Download Option for Redacted Transcript
            redacted_bytes = combined_text.encode("utf-8")
            st.download_button(
                label="Download Redacted Transcript",
                data=BytesIO(redacted_bytes),
                file_name="redacted_transcript.txt",
                mime="text/plain",
            )

    elif media_type == "Images":
        uploaded_file = st.file_uploader("Upload your image file", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            file_name = uploaded_file.name
            uploaded_file.seek(0)
            with open(file_name, "wb") as f:
                f.write(uploaded_file.read())

            st.markdown("### Select a question or enter your own:")
            selected_prompt = st.selectbox("Choose a predefined question:", [extraction_prompt])
            custom_prompt = st.text_input("Or enter your own question:")
            prompt = custom_prompt if custom_prompt else selected_prompt

            if prompt:
                final_prompt = f"University: {selected_university}\nOrg ID: {university_details.get('Org ID', 'N/A')}\nCity: {university_details.get('City', 'N/A')}\nState: {university_details.get('State', 'N/A')}\nPrompt: {prompt}"
                file = handle_image_or_file_upload(file_name, model, config)
                response = upload_and_generate(model, config, file, final_prompt)

                st.markdown("### Image Response:")
                st.write(response)

                # ✅ Add CSV Download Functionality for Image Processing
                try:
                    response_df = pd.read_csv(BytesIO(response.encode('utf-8')), sep="|")
                    response_df = response_df.loc[:, ~response_df.columns.str.contains('^Unnamed')]
                    response_df = response_df[~response_df.apply(lambda row: row.astype(str).str.contains("---").any(), axis=1)]
                    
                    csv_response_data = response_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download as CSV",
                        data=csv_response_data,
                        file_name="image_extracted_data.csv",
                        mime="text/csv",
                    )
                except Exception as e:
                    st.warning("The response could not be converted to CSV. Please ensure it is tabular data.")

if __name__ == "__main__":
    load_dotenv()
    api_key = os.environ.get("GOOGLE_API_KEY_NEW")
    if not api_key:
        raise ValueError("API key not found. Please set 'GOOGLE_API_KEY_NEW' in your environment variables.")
    genai.configure(api_key=api_key)
    main()
