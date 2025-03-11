"""
National Insurance Form Analyzer - Streamlit Application

This is the main application file that provides a user interface for uploading
National Insurance (ביטוח לאומי) forms, extracting text using OCR, and then
extracting structured data from the text using Azure OpenAI.

The application flow:
1. User uploads a PDF or image file
2. OCR is performed using Azure Document Intelligence
3. Text is extracted from the OCR result
4. Form fields are extracted using Azure OpenAI
5. Extracted data is validated using Pydantic models
6. Results are displayed in a structured JSON format

The application supports both Hebrew and English forms and handles right-to-left (RTL) text display appropriately.
"""

import streamlit as st
import json
from doc_intelligence import extract_text_from_result, perform_ocr
from field_extraction import extract_fields
from validation_schema import validate_extracted_data

# Set the title of the Streamlit application
st.title("ברוכים הבאים למערכת ניתוח הטפסים של הביטוח הלאומי")

# Add custom CSS for RTL support while keeping specific elements in LTR direction
st.markdown("""
<style>
    /* Set main content to RTL for Hebrew text */
    .element-container, div.stJson {
        direction: rtl;
        text-align: right;
    }
    
    /* Reset file uploader to left-to-right */
    [data-testid="stFileUploader"], [data-testid="stFileUploadDropzone"] {
        direction: ltr !important;
        text-align: left !important;
    }
    
    /* Reset file name display to left-to-right */
    .uploadedFileData {
        direction: ltr !important;
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True)

# File uploader for uploading PDF or JPG files
uploaded_file = st.file_uploader("אנא העלה את הקובץ שלך", type=["pdf", "jpg", "jpeg"])

if uploaded_file is not None:
    try:
        # Process the uploaded file with a loading indicator
        with st.spinner('אנא המתן, אני מעבד את הטופס..'):
            
            # Step 1: Perform OCR on the uploaded file
            ocr_result = perform_ocr(uploaded_file)
            
            # Step 2: Extract text from the OCR result
            extracted_text = extract_text_from_result(ocr_result)

            # Step 3: Extract structured data from the text using Azure OpenAI
            extracted_data = extract_fields(extracted_text)
            
            # Step 4: Validate the extracted data against our schema
            is_valid, validated_data, error_message = validate_extracted_data(extracted_data)
        
        # Display results based on validation outcome
        if is_valid and validated_data is not None:
            # Show validated data in a structured format
            st.subheader("להלן התוצאות:")
            st.json(validated_data)
        else:
            # Display validation error and raw data for debugging
            st.error(f"שגיאת אימות נתונים: {error_message}")
            st.subheader("הנתונים לא תקינים)")
            try:
                # Try to display as JSON if possible
                st.json(json.loads(extracted_data))
            
            except json.JSONDecodeError:
                # Fallback to plain text if not valid JSON
                st.text(extracted_data)
        
    except ValueError as e:
        st.error(f"שגיאה: {str(e)}")

