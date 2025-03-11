"""
Data Models Module

This module defines the Pydantic models used for request validation and 
data structure throughout the application. It ensures that the data 
exchanged between the frontend and backend follows a consistent schema.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class UserInfo(BaseModel):
    """
    Pydantic model for user information and conversation history.
    
    This model defines the structure of the data sent from the frontend to the backend,
    including all user personal details and their conversation history.
    
    All fields are optional because they may be filled in gradually during
    the information collection phase.
    """
    first_name: str = ""
    last_name: str = ""
    id_number: str = ""
    gender: str = ""
    age: int = 0
    hmo_name: str = ""
    hmo_card_number: str = ""
    membership_tier: str = ""
    conversation_history: List[Dict[str, Any]] = []
    