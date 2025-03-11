"""
Azure OpenAI Integration Module

This module handles all interactions with Azure OpenAI's services, providing
natural language processing capabilities to the Medical Q&A chatbot.

It includes functions for generating responses in both the information collection
and question answering phases of the chat interaction.
"""

import asyncio
import openai
import os
from dotenv import load_dotenv

from openai import AzureOpenAI
from vectorDB import get_knowledge_base

# Load environment variables from .env file
load_dotenv()

# Initialize the Azure OpenAI client with configuration from environment variables
client = AzureOpenAI(  
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),  
    api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),  
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    timeout=30,  # Set a timeout for API requests to prevent hanging
    )
    

async def get_openai_response(user_info, phase, query=None):
    """
    Generate a response from OpenAI based on user information and conversation phase.
    
    This function handles both the information collection phase and the Q&A phase,
    using different prompts and context depending on the phase.
    
    Args:
        user_info (dict): Dictionary containing user's information and conversation history
        phase (str): The conversation phase - either "info_collection" or "qna"
        query (str, optional): The user's question in Q&A phase. Defaults to None.
    
    Returns:
        str: The generated response from the OpenAI model
        
    Raises:
        ValueError: If an invalid phase is provided
    """
    
    # Prompt for the information collection phase
    info_collection_prompt = f"""You are a healthcare assistant chatbot that helps collect user information for accessing medical services.
    
    ---
    
    ## **Information Collection Requirements**
    
    ### **Required User Information**
    You need to collect the following information from the user in a friendly, conversational manner:
    1. First and last name
    2. ID number (must be a valid 9-digit number)
    3. Gender (must be one of: male | female)
    4. Age (must be between 0 and 120)
    5. HMO name (must be one of: מכבי | מאוחדת | כללית) - These are Israeli health funds
    6. HMO card number (must be a 9-digit number)
    7. Insurance membership tier (must be one of: זהב | כסף | ארד) 
    
    
    ## **Conversation Guidelines**
    
    1. **Language Adaptation**
       - Respond in the same language the user uses (Hebrew or English)
       - Be mindful of right-to-left formatting when responding in Hebrew
     
    3. **Information Validation**
       - Validate each piece of information as it's provided
       - If the information is invalid, politely explain why and ask again
    
    4. **Process Flow**
       - Start by asking for first and last name if that information is not provided
       - Always check what information is missing and ask for the next required piece of information
       - After collecting all information, provide a summary with "Here's a summary of your information:" (or in Hebrew: "הנה סיכום המידע שלך:") and ask the user to confirm
       - Be friendly and polite and refer to the user using his first name.

    ### **Current User Information**
    - First name: {user_info.get("first_name", "")}
    - Last name: {user_info.get("last_name", "")}
    - ID number: {user_info.get("id_number", "")}
    - Gender: {user_info.get("gender", "")}
    - Age: {user_info.get("age", 0)}
    - HMO name: {user_info.get("hmo_name", "")}
    - HMO card number: {user_info.get("hmo_card_number", "")}
    - Membership tier: {user_info.get("membership_tier", "")}
    
    ---
    
    Previous conversation history (for context):
    {user_info.get("conversation_history", [])}
    """
        
    # Choose the prompt based on the conversation phase
    if phase == "info_collection":
        prompt = info_collection_prompt
    elif phase == "qna":
        # Retrieve relevant knowledge based on the user's query
        context = get_knowledge_base(query)
        
        # Format the context from the knowledge base for better readability
        formatted_context = ""
        for i, doc in enumerate(context):
            doc_name, doc_content = doc
            formatted_context += f"Document {i+1} ({doc_name}):\n{doc_content}\n\n"
        
        # Check for special instructions
        special_instruction = user_info.get("special_instruction", "")
        
        # Get the HMO and membership tier with proper fallbacks
        hmo_name = user_info.get("hmo_name", "")
        membership_tier = user_info.get("membership_tier", "")
            
        # Prompt for the Q&A phase with user's details and retrieved knowledge
        prompt = f"""
        You are a medical services assistant chatbot specializing in Israeli health funds (קופות חולים).
        
        ---
        
        ## **Task Instructions**
        
        1. **Knowledge Source Constraints**
           - Use ONLY the knowledge base information to answer the question
           - Do not use your general knowledge unless it's to provide structure to information found in the knowledge base
        
        2. **Personalization Requirements**
           - Focus specifically on information relevant to the user's HMO ({hmo_name})
           - Prioritize details about the user's membership tier ({membership_tier})
           - When information varies by membership tier, highlight what applies to the user's specific tier
        
        3. **Response Format**
           - Respond in the same language the user used (Hebrew or English)
           - Format Hebrew text properly with right-to-left (RTL) considerations
           - Be concise, clear, and helpful
        
        4. **Knowledge Limitations**
           - If the knowledge base doesn't contain information to answer the question, politely state that you don't have that information
           - Never make up information not present in the knowledge base
        
        {special_instruction}
        
        ---
        
        ## **User Profile**
        - Name: {user_info.get("first_name", "")} {user_info.get("last_name", "")}
        - HMO: {hmo_name}
        - Membership Tier: {membership_tier}
        
        ---

        ## **User Question**:
        {query}
        
        ---
        
        ## **Knowledge Base**:
        {formatted_context}
        """
    else:
        raise ValueError(f"Invalid phase: {phase}")

    # Prepare the chat prompt with system and conversation messages
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
    
    # Add the conversation history to the messages
    for message in user_info["conversation_history"]:
        if message["role"] == "user":
            messages.append({"role": "user", "content": [{"type": "text","text": message["content"]}]})
        elif message["role"] == "system":
            messages.append({"role": "assistant", "content": [{"type": "text","text": message["content"]}]})
             
    # Make the API call asynchronously to prevent blocking
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
        messages=messages,
        max_tokens=500,
        timeout=30
    )

    # Return the generated response text
    return response.choices[0].message.content

