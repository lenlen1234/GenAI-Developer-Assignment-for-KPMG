"""
Medical Q&A Bot - Streamlit Frontend (Simplified Version)

This module implements a simplified frontend for the Medical Q&A Bot using Streamlit.
It provides a clean chat interface for users to interact with the LLM-powered bot,
which handles the entire conversation flow and information collection process.

The frontend maintains minimal state and sends all user messages to the backend LLM,
which is responsible for maintaining context, asking appropriate questions,
and collecting user information.
"""

import streamlit as st
import requests
from typing import Dict, List, Any

# Configure the page layout
st.set_page_config(layout="wide", page_title="Medical Q&A Bot")

# Custom styling
st.markdown("""
<style>
    .rtl-text {
        direction: rtl;
        text-align: right;
        width: 100%;
    }
    .main-header {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Display the main header
st.markdown('<div class="main-header">Medical Q&A Bot</div>', unsafe_allow_html=True)

# Function to detect Hebrew text
def contains_hebrew(text):
    """Check if the text contains Hebrew characters."""
    hebrew_range = range(0x0590, 0x05FF)
    return any(ord(char) in hebrew_range for char in text)

# Initialize session state for conversation history
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []
    # Add initial system message with the Hebrew greeting
    st.session_state["conversation_history"].append({
        "role": "assistant", 
        "content": "היי, אני הבוט לענייני קופות חולים. על מנת שאוכל לענות לך בצורה הטובה ביותר אשמח אם תוכל לנדב מספר פרטים עליך. נתחיל בשם (פרטי ושם משפחה). אנא הקלד בתיבה מטה:"
    })

# Initialize minimal user information structure
if "user_info" not in st.session_state:
    st.session_state["user_info"] = {
        "first_name": "",
        "last_name": "",
        "id_number": "",
        "gender": "",
        "age": 0,
        "hmo_name": "",
        "hmo_card_number": "",
        "membership_tier": "",
        "conversation_history": []
    }

# Flag to track if we're processing a message to prevent duplicate calls
if "processing" not in st.session_state:
    st.session_state["processing"] = False

# Function to ensure correct HMO and tier are set
def ensure_correct_user_info():
    """Scan conversation history to extract and set correct HMO and membership tier"""
    # Check if we've already found summary information
    summary_shown = any("הנה סיכום המידע שלך" in msg["content"] or "Here's a summary of your information" in msg["content"] 
                      for msg in st.session_state["conversation_history"])
    
    if not summary_shown:
        return  # Skip if we're still in info collection phase
    
    # Track if we found direct responses
    direct_hmo_found = False
    direct_tier_found = False
    
    # First, check for direct answers to HMO and tier questions
    for i, msg in enumerate(st.session_state["conversation_history"]):
        # Check for HMO question and answer
        if (not direct_hmo_found and msg["role"] == "assistant" and 
            any(phrase in msg["content"] for phrase in ["שם קופת החולים", "HMO name", "איזו קופת חולים"])):
            if i+1 < len(st.session_state["conversation_history"]) and st.session_state["conversation_history"][i+1]["role"] == "user":
                user_response = st.session_state["conversation_history"][i+1]["content"].lower()
                if "כללית" in user_response:
                    st.session_state["user_info"]["hmo_name"] = "כללית"
                    direct_hmo_found = True
                    
                elif "מכבי" in user_response:
                    st.session_state["user_info"]["hmo_name"] = "מכבי"
                    direct_hmo_found = True
                    
                elif "מאוחדת" in user_response:
                    st.session_state["user_info"]["hmo_name"] = "מאוחדת"
                    direct_hmo_found = True
                   
                elif "לאומית" in user_response:
                    st.session_state["user_info"]["hmo_name"] = "לאומית"
                    direct_hmo_found = True
                    
        
        # Check for membership tier question and answer
        if (not direct_tier_found and msg["role"] == "assistant" and 
            any(phrase in msg["content"] for phrase in ["רמת חברות", "סוג ביטוח", "membership tier", "סוג חברות"])):
            if i+1 < len(st.session_state["conversation_history"]) and st.session_state["conversation_history"][i+1]["role"] == "user":
                user_response = st.session_state["conversation_history"][i+1]["content"].lower()
                if "ארד" in user_response or "bronze" in user_response:
                    st.session_state["user_info"]["membership_tier"] = "ארד"
                    direct_tier_found = True
                    
                elif "כסף" in user_response or "silver" in user_response:
                    st.session_state["user_info"]["membership_tier"] = "כסף"
                    direct_tier_found = True
                    
                elif "זהב" in user_response or "gold" in user_response:
                    st.session_state["user_info"]["membership_tier"] = "זהב"
                    direct_tier_found = True
                    
    
    # If we couldn't find direct answers, try to extract from summary
    if not direct_hmo_found or not direct_tier_found:
        for msg in st.session_state["conversation_history"]:
            if "הנה סיכום המידע שלך" in msg["content"] or "Here's a summary" in msg["content"]:
                # Extract HMO if needed
                if not direct_hmo_found:
                    if "קופת חולים: כללית" in msg["content"] or "HMO: כללית" in msg["content"]:
                        st.session_state["user_info"]["hmo_name"] = "כללית"
                        
                    elif "קופת חולים: מכבי" in msg["content"] or "HMO: מכבי" in msg["content"]:
                        st.session_state["user_info"]["hmo_name"] = "מכבי"
                        
                    elif "קופת חולים: מאוחדת" in msg["content"] or "HMO: מאוחדת" in msg["content"]:
                        st.session_state["user_info"]["hmo_name"] = "מאוחדת"
                        
                    elif "קופת חולים: לאומית" in msg["content"] or "HMO: לאומית" in msg["content"]:
                        st.session_state["user_info"]["hmo_name"] = "לאומית"
                        
                
                # Extract tier if needed
                if not direct_tier_found:
                    if "רמת חברות: ארד" in msg["content"] or "Membership Tier: ארד" in msg["content"]:
                        st.session_state["user_info"]["membership_tier"] = "ארד"
                        
                    elif "רמת חברות: כסף" in msg["content"] or "Membership Tier: כסף" in msg["content"]:
                        st.session_state["user_info"]["membership_tier"] = "כסף"
                        
                    elif "רמת חברות: זהב" in msg["content"] or "Membership Tier: זהב" in msg["content"]:
                        st.session_state["user_info"]["membership_tier"] = "זהב"
                       
    
    # Print debug info about user info state
    print(f"USER INFO STATUS: HMO='{st.session_state['user_info'].get('hmo_name', '')}', tier='{st.session_state['user_info'].get('membership_tier', '')}'")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state["conversation_history"]:
        role = message["role"]
        content = message["content"]
        is_hebrew = contains_hebrew(content)
        
        with st.chat_message(role):
            if is_hebrew:
                st.markdown(f'<div class="rtl-text">{content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(content, unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Your response")
if user_input and not st.session_state["processing"]:
    # Set processing flag to prevent duplicate processing
    st.session_state["processing"] = True
    
    # Add user message to conversation history
    st.session_state["conversation_history"].append({"role": "user", "content": user_input})
    
    # Display user message immediately
    with st.chat_message("user"):
        if contains_hebrew(user_input):
            st.markdown(f'<div class="rtl-text">{user_input}</div>', unsafe_allow_html=True)
        else:
            st.markdown(user_input)
    
    # CRITICAL: Ensure correct user info is set by scanning conversation history
    ensure_correct_user_info()
    
    # Prepare the request to the backend
    # Include the full conversation history for context
    request_data = st.session_state["user_info"].copy()
    request_data["conversation_history"] = st.session_state["conversation_history"]
    
    
    # Show a spinner while waiting for response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Determine which endpoint to use based on what we have so far
                summary_shown = any("הנה סיכום המידע שלך" in msg["content"] or "Here's a summary of your information" in msg["content"] 
                      for msg in st.session_state["conversation_history"])
                
                # Check if this is a confirmation message
                is_confirmation = False
                if summary_shown and not any("תודה על האישור" in msg["content"] or "Thank you for confirming" in msg["content"] 
                        for msg in st.session_state["conversation_history"]):
                    # Common confirmation keywords in Hebrew and English
                    confirmation_keywords = ["כן", "נכון", "מאשר", "מדויק", "yes", "correct", "confirmed", "right"]
                    is_confirmation = any(keyword in user_input.lower() for keyword in confirmation_keywords)
                
                # If this is a confirmation, handle it directly to ensure proper HMO reference
                if is_confirmation:
                    # Get HMO name and membership tier from user info
                    hmo_name = st.session_state["user_info"].get("hmo_name", "")
                    membership_tier = st.session_state["user_info"].get("membership_tier", "")
                    
                    # FINAL CHECK: Scan conversation history to ensure correct information
                    ensure_correct_user_info()
                    # Get updated values after the check
                    hmo_name = st.session_state["user_info"].get("hmo_name", "")
                    membership_tier = st.session_state["user_info"].get("membership_tier", "")
                    
                  
                    
                    # Generate appropriate response based on language
                    if contains_hebrew(user_input):
                        if hmo_name:
                            assistant_response = f"תודה על האישור. אשמח לענות על שאלות שלך בנוגע לשירותים הרפואיים של קופת החולים {hmo_name}. במה אוכל לעזור לך?"
                        else:
                            assistant_response = "תודה על האישור. אשמח לענות על שאלות שלך בנוגע לשירותים הרפואיים של קופת החולים שלך. במה אוכל לעזור לך?"
                    else:
                        if hmo_name:
                            assistant_response = f"Thank you for confirming. I'll be happy to answer your questions about the medical services of {hmo_name}. How can I help you?"
                        else:
                            assistant_response = "Thank you for confirming. I'll be happy to answer your questions about medical services. How can I help you?"
                    
                    # Add response to conversation history
                    st.session_state["conversation_history"].append({
                        "role": "assistant", 
                        "content": assistant_response
                    })
                    
                    # Display the assistant response
                    if contains_hebrew(assistant_response):
                        st.markdown(f'<div class="rtl-text">{assistant_response}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(assistant_response, unsafe_allow_html=True)
                        
                    # Set endpoint to QA for future messages
                    endpoint = "qa"
                    
                else:
                    # Determine which endpoint to use
                    endpoint = "qa" if summary_shown else "collect_info"
                    
                    # For QA endpoint, ensure correct user info is being sent
                    if endpoint == "qa":
                        # Make sure we have correct values for HMO and tier in the request data
                        request_data["hmo_name"] = st.session_state["user_info"].get("hmo_name", "")
                        request_data["membership_tier"] = st.session_state["user_info"].get("membership_tier", "")
                        
                    # Make the API request with proper error handling
                    try:
                        response = requests.post(
                            f"http://localhost:8000/{endpoint}",
                            json=request_data,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            response_data = response.json()
                            assistant_response = response_data.get("response", "")
                            
                            # If we received updated user info, update our session state
                            if "updated_info" in response_data:
                                st.session_state["user_info"].update(response_data["updated_info"])
                                # Ensure our current values don't get overwritten for HMO and tier in QA mode
                                if endpoint == "qa":
                                    if st.session_state["user_info"].get("hmo_name", "") != request_data["hmo_name"]:
                                        st.session_state["user_info"]["hmo_name"] = request_data["hmo_name"]
                                    if st.session_state["user_info"].get("membership_tier", "") != request_data["membership_tier"]:
                                        st.session_state["user_info"]["membership_tier"] = request_data["membership_tier"]
                            
                            # Add assistant response to conversation history
                            st.session_state["conversation_history"].append({
                                "role": "assistant", 
                                "content": assistant_response
                            })
                            
                            # Display the assistant response
                            if contains_hebrew(assistant_response):
                                st.markdown(f'<div class="rtl-text">{assistant_response}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(assistant_response, unsafe_allow_html=True)
                        else:
                            error_message = f"Error: {response.status_code} - {response.text}"
                            st.error(error_message)
                    except requests.exceptions.RequestException as req_error:
                        st.error(f"Network error: {str(req_error)}")
                    except Exception as req_error:
                        st.error(f"Error processing request: {str(req_error)}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Clear the processing flag
    st.session_state["processing"] = False