from openai import AzureOpenAI  
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

def extract_fields(text):
    """
    Extract specific fields from the given text using Azure OpenAI client.

    Args:
        text (str): The form text to extract fields from.

    Returns:
        str: The extracted fields in JSON format.
    """
    
    try:
        # Create an instance of the AzureOpenAI client 
        client = AzureOpenAI(  
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),  
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            timeout=30,  # Add a 60-second timeout for API calls
        )
        
    except ValueError as e:
        raise ValueError(f"Error creating AzureOpenAI client: {e}")
    
    # Define the JSON format for the extracted fields
    eng_json_format = {
      "lastName": "",
      "firstName": "",
      "idNumber": "",
      "gender": "",
      "dateOfBirth": {
        "day": "",
        "month": "",
        "year": ""
      },
      "address": {
        "street": "",
        "houseNumber": "",
        "entrance": "",
        "apartment": "",
        "city": "",
        "postalCode": "",
        "poBox": ""
      },
      "landlinePhone": "",
      "mobilePhone": "",
      "jobType": "",
      "dateOfInjury": {
        "day": "",
        "month": "",
        "year": ""
      },
      "timeOfInjury": "",
      "accidentLocation": "",
      "accidentAddress": "",
      "accidentDescription": "",
      "injuredBodyPart": "",
      "signature": "",
      "formFillingDate": {
        "day": "",
        "month": "",
        "year": ""
      },
      "formReceiptDateAtClinic": {
        "day": "",
        "month": "",
        "year": ""
      },
      "medicalInstitutionFields": {
        "healthFundMember": "",
        "natureOfAccident": "",
        "medicalDiagnoses": ""
      }
    }
    
    heb_json_format = {
      "שם משפחה": "",
      "שם פרטי": "",
      "מספר זהות": "",
      "מין": "",
      "תאריך לידה": {
        "יום": "",
        "חודש": "",
        "שנה": ""
      },
      "כתובת": {
        "רחוב": "",
        "מספר בית": "",
        "כניסה": "",
        "דירה": "",
        "ישוב": "",
        "מיקוד": "",
        "תא דואר": ""
      },
      "טלפון קווי": "",
      "טלפון נייד": "",
      "סוג העבודה": "",
      "תאריך הפגיעה": {
        "יום": "",
        "חודש": "",
        "שנה": ""
      },
      "שעת הפגיעה": "",
      "מקום התאונה": "",
      "כתובת מקום התאונה": "",
      "תיאור התאונה": "",
      "האיבר שנפגע": "",
      "חתימה": "",
      "תאריך מילוי הטופס": {
        "יום": "",
        "חודש": "",
        "שנה": ""
      },
      "תאריך קבלת הטופס בקופה": {
        "יום": "",
        "חודש": "",
        "שנה": ""
      },
      "למילוי ע\"י המוסד הרפואי": {
        "חבר בקופת חולים": "",
        "מהות התאונה": "",
        "אבחנות רפואיות": ""
      }
    }

    # Create the prompt for the Azure OpenAI model
    prompt=f"""
    You are an AI assistant that extracts specific fields from text originated from ביטוח לאומי (National Insurance Institute) forms. 
    ---

    ## **Instructions**:
    1. **Detect the Language**  
    - First, determine if the form is written in **Hebrew** or **English**.  
    - Hebrew forms are right-to-left (RTL).  

    2. **Extract Required Fields**  
    - Extract the following fields from the text and provide the output in the specified JSON format.
    - Identify and extract all required fields from the provided text.  
    - Return the extracted information in JSON format.  
    - Use the **Hebrew JSON format** below for Hebrew forms and the **English JSON format** for English forms.  

    4. **Hebrew Language Considerations**  
    - Remember that Hebrew text is structured right to left (RTL).  
    - Ensure correct word order and alignment when processing Hebrew text.  

    5. **Phone Number Extraction**  
    - Both "טלפון קווי" (Landline Phone Number) and "טלפון נייד" (Mobile Phone Number) must be extracted correctly.  
    - Both Phone numbers always start with 0. If the first digit is 6 or 8, assume it's an OCR mistake and should be a 0 instead
    - The "טלפון נייד" (Mobile Phone Number) should be a 10-digit number starting with "05".
    - Ensure no extra spaces, symbols, or misrecognized characters in the extracted number.  
    
    5. **Handling Missing Data**  
    - If any fields are not present or not extractable, use an empty string in the JSON output.
    
    ---

    ## **Examples**:
    ### **Example 1: Address Extraction**
    #### Input Text:
  "     כתובת
  מיקוד
  יישוב
  דירה
  כניסה
  מס׳ בית
  4454124
  יוקנעם :unselected:
  34
  6
  6 5|544 1 2 7|4 2
  טלפון נייד
  רחוב / תא דואר
  חיים ויצמן
  טלפון קווי
  0 97 6 | 5 6 | 0 5 4 " 

  #### Expected JSON Output: 

  "כתובת": 
    "רחוב": "חיים ויצמן",
    "מספר בית": "6",
    "כניסה": "",
    "דירה": "34",
    "ישוב": "יוקנעם",
    "מיקוד": "4454124",
    "תא דואר": ""
  ,
  "טלפון קווי": "097656054",
  "טלפון נייד": "0554412742",
  "
  
  ### **Example 2: Date Extraction**
  #### Input Text:
  " תאריך מילוי הטופס/n2| 005199 9/nתאריך קבלת הטופס בקופה/n3 00619 9 9/nיום/nחודש/n "
  
  #### Expected JSON Output: 

  "תאריך מילוי הטופס": 
          "יום": "20",
        "חודש": "05",
        "שנה": "1999"
    ,
    "תאריך קבלת הטופס בקופה": 
        "יום": "30",
        "חודש": "06",
        "שנה": "1999"
    ,
    #### input_text:
    "ת.ז.\nס״ב\n0|3 |3 |4 5 | 2 1 |5 6 7\n"

    #### expected output:
    "מספר זהות": "0334521567",
   
    ## **Input Data**:
    - Extract fields from the following text:
    {text}

    ## **Output Format**:
    ### English format:
    {str(eng_json_format)}

    ### Hebrew format:
    {str(heb_json_format)}
    """
    
    
    #Prepare the messages array
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ] 

    try:
        # Generate response using azure openai client, GPT-4o model
        # Temperature is set to 0 to ensure the model is deterministic
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_MODEL"),
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"}  
        )

        # Extract the JSON response and parse it to ensure valid JSON
        extracted_data_str = response.choices[0].message.content
        
        # Attempt to validate and clean the JSON if needed
        try:
            # Parse and re-serialize to ensure clean JSON
            extracted_data = json.loads(extracted_data_str)
            extracted_data = json.dumps(extracted_data, ensure_ascii=False)
        
        except json.JSONDecodeError:
            # If parsing fails, return an error message
            raise ValueError("Failed to parse JSON from the model response")
    
    except Exception as e:
        raise ValueError(f"Error generating response from Azure OpenAI: {e}")

    return extracted_data
