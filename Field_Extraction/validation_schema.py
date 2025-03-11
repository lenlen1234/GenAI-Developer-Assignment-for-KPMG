"""
Validation Schema for National Insurance Form Data.

This module provides Pydantic models and validation functions for ensuring the
extracted data from National Insurance forms is properly formatted and contains
valid information. It supports both Hebrew and English form formats.

The module defines:
1. Pydantic models for form elements (dates, addresses, etc.)
2. Full form models for both Hebrew and English formats
3. Validation functions with specific field validators
4. A central validation function that processes extracted JSON data
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, Optional, Union, Any
import re
import json

# Common models for both languages
class DateModel(BaseModel):
    """Date model with day, month, and year fields."""
    day: str = Field(default="")
    month: str = Field(default="")
    year: str = Field(default="")

class AddressModel(BaseModel):
    """Address model for English forms."""
    street: str = Field(default="")
    houseNumber: str = Field(default="")
    entrance: str = Field(default="")
    apartment: str = Field(default="")
    city: str = Field(default="")
    postalCode: str = Field(default="")
    poBox: str = Field(default="")

class MedicalInstitutionModel(BaseModel):
    """Medical institution information for English forms."""
    healthFundMember: str = Field(default="")
    natureOfAccident: str = Field(default="")
    medicalDiagnoses: str = Field(default="")

class EnglishFormModel(BaseModel):
    """Model for English form data."""
    lastName: str = Field(default="")
    firstName: str = Field(default="")
    idNumber: str = Field(default="")
    gender: str = Field(default="")
    dateOfBirth: DateModel = Field(default_factory=DateModel)
    address: AddressModel = Field(default_factory=AddressModel)
    landlinePhone: str = Field(default="")
    mobilePhone: str = Field(default="")
    jobType: str = Field(default="")
    dateOfInjury: DateModel = Field(default_factory=DateModel)
    timeOfInjury: str = Field(default="")
    accidentLocation: str = Field(default="")
    accidentAddress: str = Field(default="")
    accidentDescription: str = Field(default="")
    injuredBodyPart: str = Field(default="")
    signature: str = Field(default="")
    formFillingDate: DateModel = Field(default_factory=DateModel)
    formReceiptDateAtClinic: DateModel = Field(default_factory=DateModel)
    medicalInstitutionFields: MedicalInstitutionModel = Field(default_factory=MedicalInstitutionModel)
    
    @field_validator('idNumber')
    def validate_id_number(cls, v):
        if v and not v.isdigit():
            raise ValueError('ID number must contain only digits')
        return v
        
    @field_validator('mobilePhone', 'landlinePhone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\d+$', v):
            raise ValueError('Phone number must contain only digits')
        return v

class HebrewDateModel(BaseModel):
    """Date model with Hebrew field names."""
    יום: str = Field(default="")
    חודש: str = Field(default="")
    שנה: str = Field(default="")

class HebrewAddressModel(BaseModel):
    """Address model with Hebrew field names."""
    רחוב: str = Field(default="")
    מספר_בית: str = Field(alias="מספר בית", default="")
    כניסה: str = Field(default="")
    דירה: str = Field(default="")
    ישוב: str = Field(default="")
    מיקוד: str = Field(default="")
    תא_דואר: str = Field(alias="תא דואר", default="")

class HebrewMedicalInstitutionModel(BaseModel):
    """Medical institution information with Hebrew field names."""
    חבר_בקופת_חולים: str = Field(alias="חבר בקופת חולים", default="")
    מהות_התאונה: str = Field(alias="מהות התאונה", default="")
    אבחנות_רפואיות: str = Field(alias="אבחנות רפואיות", default="")

class HebrewFormModel(BaseModel):
    """Model for Hebrew form data."""
    שם_משפחה: str = Field(alias="שם משפחה", default="")
    שם_פרטי: str = Field(alias="שם פרטי", default="")
    מספר_זהות: str = Field(alias="מספר זהות", default="")
    מין: str = Field(default="")
    תאריך_לידה: HebrewDateModel = Field(alias="תאריך לידה", default_factory=HebrewDateModel)
    כתובת: HebrewAddressModel = Field(default_factory=HebrewAddressModel)
    טלפון_קווי: str = Field(alias="טלפון קווי", default="")
    טלפון_נייד: str = Field(alias="טלפון נייד", default="")
    סוג_העבודה: str = Field(alias="סוג העבודה", default="")
    תאריך_הפגיעה: HebrewDateModel = Field(alias="תאריך הפגיעה", default_factory=HebrewDateModel)
    שעת_הפגיעה: str = Field(alias="שעת הפגיעה", default="")
    מקום_התאונה: str = Field(alias="מקום התאונה", default="")
    כתובת_מקום_התאונה: str = Field(alias="כתובת מקום התאונה", default="")
    תיאור_התאונה: str = Field(alias="תיאור התאונה", default="")
    האיבר_שנפגע: str = Field(alias="האיבר שנפגע", default="")
    חתימה: str = Field(default="")
    תאריך_מילוי_הטופס: HebrewDateModel = Field(alias="תאריך מילוי הטופס", default_factory=HebrewDateModel)
    תאריך_קבלת_הטופס_בקופה: HebrewDateModel = Field(alias="תאריך קבלת הטופס בקופה", default_factory=HebrewDateModel)
    למילוי_ע_י_המוסד_הרפואי: HebrewMedicalInstitutionModel = Field(alias='למילוי ע"י המוסד הרפואי', default_factory=HebrewMedicalInstitutionModel)
    
    @field_validator('מספר_זהות')
    def validate_id_number(cls, v):
        if v and not v.isdigit():
            raise ValueError('מספר זהות חייב להכיל רק ספרות')
        return v
        
    @field_validator('טלפון_נייד', 'טלפון_קווי')
    def validate_phone(cls, v):
        if v and not re.match(r'^\d+$', v):
            raise ValueError('מספר טלפון חייב להכיל רק ספרות')
        return v
    
    model_config = {
        "populate_by_name": True
    }

def validate_extracted_data(data_str: str) -> tuple[bool, Optional[dict], str]:
    """
    Validate the extracted data against the defined schemas.
    
    This function takes a JSON string containing extracted form data and validates it
    against the appropriate Pydantic model (Hebrew or English). It determines which
    schema to use based on the presence of specific keys in the data.
    
    The function provides:
    - Data validation against the correct schema
    - Type checking for specific fields (like ID numbers)
    - Complete model instantiation with default values for missing fields
    - Proper handling of field aliases for Hebrew field names
    
    Args:
        data_str (str): JSON string of the extracted data from the form
    
    Returns:
        tuple[bool, Optional[dict], str]: A tuple containing:
            - is_valid (bool): True if validation passed, False otherwise
            - validated_data (Optional[dict]): The validated data with proper structure 
              or None if validation failed
            - error_message (str): Error message if validation failed, empty string otherwise
    
    Raises:
        No exceptions are raised as they are caught and returned as error messages
    """
    try:
        # Parse the JSON string to dict
        data_dict = json.loads(data_str) if isinstance(data_str, str) else data_str
        
        # Check if we have Hebrew or English keys to determine format
        hebrew_keys = {"שם משפחה", "שם פרטי", "מספר זהות"}
        english_keys = {"lastName", "firstName", "idNumber"}
        
        validated_data = None
        
        if any(key in data_dict for key in hebrew_keys):
            # Hebrew format
            hebrew_model = HebrewFormModel.model_validate(data_dict)
            # Convert model to dict, preserving aliases for output
            validated_data = hebrew_model.model_dump(by_alias=True)
                
        elif any(key in data_dict for key in english_keys):
            # English format
            english_model = EnglishFormModel.model_validate(data_dict)
            validated_data = english_model.model_dump()
            
        if validated_data:
            return True, validated_data, ""
        else:
            return False, None, "לא זוהה מבנה תקין של נתונים: חסרים שדות זיהוי"
        
    except json.JSONDecodeError as e:
        return False, None, f"שגיאת JSON: {str(e)}"
    except ValueError as e:
        return False, None, f"שגיאת אימות: {str(e)}"
    except Exception as e:
        return False, None, f"שגיאה: {str(e)}"


# Potential Future Improvements:
# ------------------------------
# 1. Advanced Validation:
#    - Implement proper Israeli ID validation algorithm (check digit verification)
#    - Add stronger validation for addresses (verify city/postal code combinations)
#    - Add date range validations (e.g., birthdate cannot be in the future)
#
# 2. External Validation:
#    - Integrate with external APIs to verify addresses against geographic databases
#    - Validate phone numbers against Israeli phone number patterns
#    - Check existence of ID numbers against public databases where legally permitted
#
# 3. LLM Re-verification:
#    - Send validated data back to an LLM for logical consistency checking
#    - Have the LLM suggest fixes for potential errors or inconsistencies
#    - Implement confidence scores for each extracted field
#
# 4. Schema Improvements:
#    - Add more specific field types (e.g., enum for gender options)
#    - Implement relationship validations between fields
#    - Support partial validation for forms with missing sections 