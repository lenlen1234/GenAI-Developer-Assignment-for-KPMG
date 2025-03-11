"""
Vector Database Module

This module implements a vector-based knowledge retrieval system using FAISS 
for efficient similarity search. It processes text documents into embeddings
and allows for semantic search based on user queries.

The module handles:
1. Generating embeddings for text using Azure OpenAI's embedding model
2. Loading and indexing HTML documents from the knowledge base
3. Retrieving the most relevant documents for a given query
"""

import os
import faiss
import numpy as np
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_embeddings(text):
    """
    Generate embedding vectors for the given text using Azure OpenAI's embedding model.
    
    Args:
        text (str): The text to generate embeddings for
        
    Returns:
        numpy.ndarray: A 1xN numpy array containing the embedding vector
        
    Note:
        The embedding dimension is determined by the model used (text-embedding-3-large-2)
        which produces 3072-dimensional vectors.
    """
    # Initialize Azure OpenAI client with embedding model configuration
    openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT"), 
    api_key=os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY"), 
    api_version=os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION"))
    
    # Generate embeddings using the configured model
    response = openai_client.embeddings.create(
        input = text,
        model= os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"))
    
    # Extract and reshape the embedding vector
    embeddings = response.model_dump()
    return np.array(embeddings['data'][0]['embedding'], dtype=np.float32).reshape(1, -1)


# Initialize FAISS index with the correct embedding dimension
# The dimension is set to None initially and will be determined dynamically
# from the first embedding generated
embedding_dimension = None
index = None  # Initialize index after we know the embedding dimension

def load_knowledge_base():
    """
    Load HTML documents from the knowledge base directory and index them in FAISS.
    
    This function:
    1. Reads all HTML files from the knowledge base directory
    2. Generates embeddings for each document
    3. Adds the embeddings to the FAISS index
    4. Returns a list of (filename, content) tuples for later retrieval
    
    Returns:
        list: A list of tuples containing (filename, document_content)
        
    Raises:
        ValueError: If directory doesn't exist or contains no HTML files
    """
    global embedding_dimension, index
    
    documents = []
    # Use the hardcoded path that works in the current environment
    directory = "./phase2_data"
    
    # If directory doesn't exist, raise an error
    if not os.path.exists(directory):
        raise ValueError(f"Knowledge base directory not found: {directory}")
    
    # Log the directory path being used
    print(f"Loading knowledge base from: {os.path.abspath(directory)}")
    
    # Read all HTML files in the directory
    html_files = [f for f in os.listdir(directory) if f.endswith(".html")]
    if not html_files:
        raise ValueError(f"No HTML files found in {directory}")
        
    for filename in html_files:
        file_path = os.path.join(directory, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            documents.append((filename, content))
    
    # Generate embeddings for the documents and add them to the FAISS index
    embeddings = []
    
    for doc in documents:
        # Generate the first embedding to determine the dimension
        embedding = generate_embeddings(doc[1])
        
        # If this is the first embedding, detect the dimension and initialize the index
        if embedding_dimension is None:
            embedding_dimension = embedding.shape[1]
            print(f"Detected embedding dimension: {embedding_dimension}")
            index = faiss.IndexFlatL2(embedding_dimension)
            
        embeddings.append(embedding)
    
    # Add all embeddings to the FAISS index
    index.add(np.vstack(embeddings))
    return documents

# Load and index the knowledge base at module initialization
knowledge_base_documents = load_knowledge_base()

def get_knowledge_base(query):
    """
    Retrieves relevant documents from the knowledge base based on the query.
    
    Performs semantic search using embeddings to find the most relevant
    documents to answer the user's question.
    
    Args:
        query (str): The user's question or query text
        
    Returns:
        list: A list of tuples containing (filename, document_content) for the 
              top 3 most relevant documents, or a default message if no 
              relevant documents are found.
    """
    # Check if query is empty or None
    if not query or query.strip() == "":
        return [("no_document.html", "Please ask a specific question about medical services.")]
    
    # Generate embedding for the query
    query_embedding = generate_embeddings(query)
    
    # Find the closest documents in the FAISS index
    # Returns top 4 most similar documents
    distances, indices = index.search(query_embedding, 4)
    
    # Get the closest documents
    closest_documents = []
    for i, idx in enumerate(indices[0]):
        if idx < len(knowledge_base_documents):
            closest_documents.append(knowledge_base_documents[idx])
    
    # If no documents were found, return a default message
    if not closest_documents:
        return [("no_document.html", "I couldn't find information related to your question in my knowledge base.")]
    
    return closest_documents

