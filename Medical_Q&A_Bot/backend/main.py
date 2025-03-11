"""
Medical Q&A Bot - FastAPI Backend

This is the main FastAPI application that serves as the backend for the Medical Q&A Bot.
It provides API endpoints for both the information collection phase and the question-answering
phase of the conversation, manages user information extraction, and handles logging.

The application is designed to be stateless, with all user information and conversation
history maintained on the client side.
"""

from fastapi import FastAPI, HTTPException
from models import UserInfo
from openai_integration import get_openai_response
import logging
from fastapi.middleware.cors import CORSMiddleware
import re
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI()

# Add CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_user_info(response_text, current_user_info):
    """
    Extract user information from conversation history.
    
    This simplified function focuses on extracting information directly from
    user responses in the conversation history rather than trying to parse
    complex LLM responses with regex.
    
    Args:
        response_text (str): The LLM's response text (not used in this simplified version)
        current_user_info (dict): The current state of user information
        
    Returns:
        dict: The updated user information with newly extracted data
    """
    updated_info = current_user_info.copy()
    
    # Skip if we don't have conversation history
    if "conversation_history" not in current_user_info or not current_user_info["conversation_history"]:
        return updated_info
        
    # Extract information from direct user responses to questions
    conversation = current_user_info["conversation_history"]
    
    # Process each assistant-user message pair
    for i, msg in enumerate(conversation):
        if msg["role"] == "assistant" and i+1 < len(conversation) and conversation[i+1]["role"] == "user":
            assistant_msg = msg["content"].lower()
            user_response = conversation[i+1]["content"].strip()
            
            # Skip empty responses
            if not user_response:
                continue
                
            # Extract name
            if any(keyword in assistant_msg for keyword in ["שם פרטי", "שם משפחה", "שם מלא", "first name", "last name", "full name"]) and not (updated_info["first_name"] and updated_info["last_name"]):
                name_parts = user_response.split()
                if len(name_parts) >= 2:
                    updated_info["first_name"] = name_parts[0]
                    updated_info["last_name"] = " ".join(name_parts[1:])
                elif len(name_parts) == 1:
                    updated_info["first_name"] = name_parts[0]
            
            # Extract ID number
            elif any(keyword in assistant_msg for keyword in ["תעודת זהות", "ת.ז.", "מספר זהות", "id number", "identification"]) and not updated_info["id_number"]:
                digits = ''.join([c for c in user_response if c.isdigit()])
                if len(digits) >= 9:
                    updated_info["id_number"] = digits[:9]
            
            # Extract gender
            elif any(keyword in assistant_msg for keyword in ["מגדר", "מין", "gender", "sex"]) and not updated_info["gender"]:
                response_lower = user_response.lower()
                if any(term in response_lower for term in ["זכר", "גבר", "male", "man"]):
                    updated_info["gender"] = "Male"
                elif any(term in response_lower for term in ["נקבה", "אישה", "female", "woman"]):
                    updated_info["gender"] = "Female"
            
            # Extract age
            elif any(keyword in assistant_msg for keyword in ["גיל", "בן כמה", "בת כמה", "age", "how old"]) and not updated_info["age"]:
                digits = ''.join([c for c in user_response if c.isdigit()])
                if digits:
                    try:
                        age = int(digits)
                        if 0 <= age <= 120:  # Reasonable age range
                            updated_info["age"] = age
                    except:
                        pass
            
            # Extract HMO name
            elif any(keyword in assistant_msg for keyword in ["קופת חולים", "hmo", "health fund"]) and not updated_info["hmo_name"]:
                response_lower = user_response.lower()
                if "מכבי" in response_lower or "maccabi" in response_lower:
                    updated_info["hmo_name"] = "מכבי"
                elif "כללית" in response_lower or "clalit" in response_lower:
                    updated_info["hmo_name"] = "כללית"
                elif "מאוחדת" in response_lower or "meuchedet" in response_lower:
                    updated_info["hmo_name"] = "מאוחדת"
                elif "לאומית" in response_lower or "leumit" in response_lower:
                    updated_info["hmo_name"] = "לאומית"
            
            # Extract HMO card number
            elif any(keyword in assistant_msg for keyword in ["מספר כרטיס", "מספר קופת חולים", "card number"]) and not updated_info["hmo_card_number"]:
                digits = ''.join([c for c in user_response if c.isdigit()])
                if len(digits) >= 8:
                    updated_info["hmo_card_number"] = digits
            
            # Extract membership tier
            elif any(keyword in assistant_msg for keyword in ["רמת חברות", "סוג ביטוח", "רמת ביטוח", "מסלול", "tier", "membership level", "insurance level"]) and not updated_info["membership_tier"]:
                response_lower = user_response.lower()
                if "זהב" in response_lower or "gold" in response_lower:
                    updated_info["membership_tier"] = "זהב"
                elif "כסף" in response_lower or "silver" in response_lower:
                    updated_info["membership_tier"] = "כסף"
                elif "ארד" in response_lower or "bronze" in response_lower:
                    updated_info["membership_tier"] = "ארד"
    
    logger.info(f"Extracted user info: {updated_info}")
    return updated_info

@app.post("/collect_info")
async def collect_info(user_info: UserInfo):
    """
    API endpoint for the information collection phase of the conversation.
    
    Receives the current state of user information and conversation history,
    passes it to the LLM, and tries to extract any new information from the response.
    
    Args:
        user_info (UserInfo): Pydantic model containing user information and conversation history
        
    Returns:
        dict: Contains the LLM response and updated user information
        
    Raises:
        HTTPException: If an error occurs during processing
    """
    try:
        logger.info("Received request for /collect_info")
        logger.info(f"Current user info state: {user_info.model_dump()}")
        
        # Get LLM response for information collection phase
        response = await get_openai_response(user_info.model_dump(), phase="info_collection")
        logger.info("OpenAI response received for info collection")
        
        # Try to extract user information from the response
        updated_info = extract_user_info(response, user_info.model_dump())
        if updated_info != user_info.model_dump():
            logger.info(f"Extracted updated user info: {updated_info}")
        
        return {"response": response, "updated_info": updated_info}
    except Exception as e:
        logger.error(f"Error in collect_info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/qa")
async def qa(user_info: UserInfo):
    """
    API endpoint for the question-answering phase of the conversation.
    
    Takes the user's question from the conversation history and user information,
    then generates a response using the knowledge base and LLM.
    
    Args:
        user_info (UserInfo): Pydantic model containing user information and conversation history
        
    Returns:
        dict: Contains the LLM's answer to the user's question
        
    Raises:
        HTTPException: If an error occurs during processing
    """
    try:
        logger.info("Received request for /qa")
        # Extract the latest user message as the query
        query = user_info.conversation_history[-1]["content"] if user_info.conversation_history else ""
        logger.info(f"Query: {query}")
        
        # Get LLM response for Q&A phase
        response = await get_openai_response(user_info.model_dump(), phase="qna", query=query)
        logger.info("OpenAI response received for Q&A")
        
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in qa: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_confirmation")
async def check_confirmation(user_info: UserInfo):
    """
    API endpoint for checking if a user response is a confirmation.
    
    Uses simple keyword matching to determine if the user's latest message is confirming 
    their information, regardless of the exact wording or language used.
    
    Args:
        user_info (UserInfo): Pydantic model containing user information and conversation history
        
    Returns:
        dict: Contains a boolean indicating if the message is a confirmation
        
    Raises:
        HTTPException: If an error occurs during processing
    """
    try:
        logger.info("Received request for /check_confirmation")
        
        # Extract the latest user message
        if not user_info.conversation_history:
            return {"is_confirmation": False}
            
        latest_message = user_info.conversation_history[-1]["content"].lower()
        logger.info(f"Checking if message is confirmation: {latest_message}")
        
        # Simple keyword matching for confirmations in Hebrew and English
        confirmation_keywords = [
            # Hebrew confirmations
            "כן", "נכון", "מאשר", "מאשרת", "מדויק", "בסדר", "מצוין", "מעולה", "סבבה",
            # English confirmations
            "yes", "correct", "confirm", "confirmed", "right", "ok", "okay", "sure", 
            "good", "fine", "perfect", "exactly", "yep", "yeah"
        ]
        
        # Check if any confirmation keyword is in the message
        is_confirmation = any(keyword in latest_message for keyword in confirmation_keywords)
        
        logger.info(f"Confirmation check result: {is_confirmation}")
        return {"is_confirmation": is_confirmation}
        
    except Exception as e:
        logger.error(f"Error in check_confirmation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: Simple status message indicating the API is healthy
    """
    return {"status": "healthy"}