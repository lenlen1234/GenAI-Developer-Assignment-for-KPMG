# National Insurance Form Extraction

This project is designed to extract specific fields from text originated from ביטוח לאומי (National Insurance Institute) forms. The application uses Azure Document Intelligence for OCR and Azure OpenAI for extracting the required fields.

## Features

- **OCR**: Uses Azure Document Intelligence to extract text from PDF and image files
- **Field Extraction**: Leverages Azure OpenAI GPT-4o to intelligently extract structured data from form text
- **Data Validation**: Validates extracted data against predefined schemas using Pydantic
- **Right-to-Left (RTL) Support**: Properly handles Hebrew text with right-to-left display
- **User-Friendly Interface**: Streamlit-based UI 

## Project Structure

- `app.py`: Streamlit application for uploading documents and displaying extracted fields
- `doc_intelligence.py`: Contains functions for performing OCR with Azure Document Intelligence client. 
- `field_extraction.py`: Contains functions for extracting specific fields from the OCR result using Azure OpenAI.
- `validation_schema.py`: Contains Pydantic models and validation functions for ensuring data quality and format
- `requirements.txt`: List of required Python packages
- `.env`: Configuration file for Azure service credentials (not included)

## Technical Details

### Form Processing Pipeline

1. **Document Upload**: Users upload PDF or image files through the Streamlit interface
2. **OCR Processing**: Azure Document Intelligence extracts text from the uploaded document
3. **Text Extraction**: The application processes the OCR result to extract raw text
4. **Field Extraction**: Azure OpenAI service identifies and extracts structured field data from the text
5. **Data Validation**: Extracted data is validated against predefined schemas
6. **Result Display**: Results are displayed in a structured JSON format with proper RTL support

### Validation System

The application includes a comprehensive validation system that:
- Validates field formats (e.g., ID numbers)
- Ensures all required fields are present
- Provides default values for missing fields
- Handles both Hebrew and English form formats
- Generates user-friendly error messages when validation fails

## Future Improvements

Several enhancements could be made to further improve the system:

### 1. Enhanced OCR Processing
- Implement more sophisticated OCR result parsing to improve extraction accuracy
- Use spatial information from the OCR results to better understand form structure
- Apply specific post-processing for Hebrew OCR to handle language-specific challenges

### 2. Advanced Validation Tools
- **External Data Verification**: Validate addresses by checking against geographic databases or web services
- **ID Number Validation**: Implement Israeli ID number (Teudat Zehut) validation algorithm
- **Phone Number Formatting**: Add region-specific phone number validation and formatting
- **Cross-field Validation**: Implement checks between related fields (e.g., city and postal code)

### 3. LLM/JLM-Powered Verification Loop
- Send extracted data back to the LLM model for re-confirmation
- Have the model identify potential inconsistencies or errors in the extracted data
- Implement an automated correction system for common extraction errors
- USE JLM for secondary model verification: Integrate Nemotron or another specialized language model for verification of Hebrew content and JSON output confirmation.

### 4. User Experience Improvements
- Allow users to manually correct extracted information
- Provide visualization of the extracted data mapped to the original document

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Azure subscription with Azure Document Intelligence and Azure OpenAI services
- Azure OpenAI deployment with GPT-4o model

### Installation

1. Download the project files to your local machine.

2. Open a terminal or command prompt and navigate to the project folder:
   ```
   cd path/to/Field_Extraction
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file with the following parameters from your Azure subscription:

```
AZURE_DOC_INTELLIGENCE_ENDPOINT=document-intelligence-endpoint
AZURE_DOC_INTELLIGENCE_API_KEY=document-intelligence-api-key
AZURE_OPENAI_ENDPOINT=azure-openai-endpoint
AZURE_OPENAI_API_KEY=azure-openai-api-key
AZURE_OPENAI_API_VERSION=azure-openai-api-version
AZURE_OPENAI_MODEL=azure-openai-model
```

### Running the Application

1. Run the Streamlit application:

    ```
    streamlit run app.py
    ```

2. A web browser will open with the application interface.

3. Upload a PDF or JPG file of a National Insurance form.

4. The application will process the form and display the extracted data as structured JSON.

## License

This project was developed by Lena, hope you find it useful and informative :)
