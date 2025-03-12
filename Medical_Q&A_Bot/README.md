# Medical Q&A Bot

A microservice-based chatbot system that answers questions about medical services for Israeli HMO (Maccabi, Meuhedet, and Clalit) based on user-specific information.

## Project Overview

This chatbot system is designed as a stateless microservice that helps users get personalized information about their health fund services. The system operates in two distinct phases:

1. **Information Collection Phase**: The chatbot collects essential information about the user, including their personal details and HMO membership information.
2. **Q&A Phase**: Using the collected information, the chatbot provides personalized answers to questions about medical services relevant to the user's HMO and membership tier.

## Architecture

The system follows a microservice architecture with the following components:

### Backend
- **FastAPI Server**: RESTful API service for processing chat requests
- **Azure OpenAI Integration**: Connection to GPT-4o for natural language processing
- **Vector Database**: FAISS-based embedding search for knowledge retrieval

### Frontend
- **Streamlit UI**: A responsive chat interface that supports both Hebrew and English
- **Client-side State Management**: All user data and conversation history is maintained on the client side

## Features

- **Bilingual Support**: Full support for both Hebrew and English with RTL for Hebrew text
- **User Information Collection**: Interactive collection and validation of user details
- **Personalized Responses**: Tailored answers based on user's health fund and membership tier
- **Knowledge Base Integration**: Responses based on health fund-specific documents
- **Responsive Design**: Chat interface works well on both desktop and mobile devices
- **Stateless Architecture**: Designed for scaling with multiple concurrent users

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Azure OpenAI API access

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/lenlen1234/GenAI-Developer-Assessment-Assignment-for-KPMG.git
   cd medical-qa-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   
   Create a `.env` file in the root directory with the following variables:
   ```
   # Azure OpenAI API Configuration
   AZURE_OPENAI_ENDPOINT=your_openai_endpoint
   AZURE_OPENAI_API_KEY=your_openai_api_key
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   AZURE_OPENAI_API_VERSION=your_api_version

   # Embedding Model API Configuration
   AZURE_OPENAI_EMBEDDING_ENDPOINT=your_embedding_endpoint
   AZURE_OPENAI_EMBEDDING_API_KEY=your_embedding_api_key
   AZURE_OPENAI_EMBEDDING_API_VERSION=your_embedding_api_version
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment
   
   # Knowledge Base Configuration
   
   The knowledge base documents are stored in the `backend/phase2_data/` directory. 

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd frontend
   streamlit run app.py
   ```

3. Open your browser and navigate to `http://localhost:8501` to access the application if it doesn't pop up automatically.

## Project Structure

```
Medical_Q&A_Bot/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── openai_integration.py # Azure OpenAI integration
│   ├── vectorDB.py          # Vector database for knowledge retrieval
│   ├── models.py            # Pydantic models for data validation
│   ├── requirements.txt     # Backend dependencies
│   └── phase2_data/         # Knowledge base HTML documents (important!)
├── frontend/
│   ├── app.py               # Streamlit UI application
│   └── requirements.txt     # Frontend dependencies
├── .env                     # Environment variables
├── requirements.txt         # Project-wide dependencies
└── README.md                # This file
```

## Usage

### Information Collection Phase
When you first start the application, the chatbot will guide you through a series of questions to collect your information:
1. First and last name
2. ID number
3. Gender
4. Age
5. HMO name (מכבי / מאוחדת / כללית)
6. HMO card number
7. Insurance membership tier (זהב / כסף / ארד)

The chatbot will validate your input and present a summary for confirmation.

### Q&A Phase
After confirming your information, you can ask any questions about medical services
The chatbot will provide answers specific to your health fund and membership tier.

## Future Improvements

If more development time were available, these enhancements would be implemented:

1. **Query Rewrite and Classification**
   - Implement an additional LLM call to handle follow-up questions
   - Develop a system to rewrite and refine user queries before searching the vector database
   - Better understand user intent by analyzing conversation context and history

2. **Enhanced Vector Database Search Mechanism**
   - Improve search relevance with better document chunking strategies
   - Implement hybrid search combining vector and keyword-based approaches
   - Add metadata filtering based on HMO and membership tier

3. **Refactor Backend Architecture**
   - Reduce hardcoded functions in main.py for greater flexibility
   - Implement a more modular approach allowing the LLM to handle more validation taskss

4. **Advanced Prompt Engineering**
   - Further optimize prompt templates for both collection and Q&A phases

