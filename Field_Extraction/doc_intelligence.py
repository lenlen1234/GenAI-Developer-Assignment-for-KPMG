from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


def perform_ocr(document):
    """
    Perform OCR on the uploaded document using Azure Document Intelligence prebuilt-layout model which is the best model for extracting data from general forms.
    Document Intelligence client is initiated with the endpoint and API key from the environment variables.

    Args:
        document (file): The uploaded document file.

    Returns:
        AnalyzeResult: The result of the OCR analysis.
    """  
    
    # Get the endpoint and API key from the environment variables
    endpoint = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT")
    api_key = os.getenv("AZURE_DOC_INTELLIGENCE_API_KEY")
    
    try:
        # Create a DocumentAnalysis Client using the endpoint and API key
        client = DocumentIntelligenceClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(api_key))
    
    except ValueError as e:
        raise ValueError(f"Error creating DocumentAnalysisClient: {e}")
    
    try:
        # Perform OCR analysis on the document using the prebuilt-layout model
        poller = client.begin_analyze_document("prebuilt-layout", document)
        result = poller.result()
        return result
    except Exception as e:
        raise ValueError(f"Error performing OCR analysis: {e}")


def extract_text_from_result(result):
    """
    Extract text from the OCR result.

    Args:
        result (AnalyzeResult): The result of the OCR analysis.

    Returns:
        str: The extracted text.
    """
    
    extracted_text = ""
    
    if not result:
        ValueError("No OCR result found.")
    
    # Extract text from the OCR result while iterating over the pages and lines
    for page in result.pages:
            for line in page.lines:
                extracted_text += line.content + "\n"
    
    return extracted_text.strip()
