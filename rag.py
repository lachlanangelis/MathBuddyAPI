# Import necessary libraries and modules
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from ollama import Client


# Function to extract context using ChromaDB
def extract_context(query):
    # Initialize ChromaDB client with the specified host, port, and settings
    chroma_client = chromadb.HttpClient(host='localhost', port=8000, settings=Settings(allow_reset=True))

    # Initialize the embedding function using a pre-trained sentence transformer model
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create a Chroma instance to interact with the database
    db = Chroma(
        client=chroma_client,
        collection_name="my_collection",  # Name of the collection in ChromaDB
        embedding_function=embedding_function,
    )

    # Perform a similarity search in the ChromaDB with the provided query
    docs = db.similarity_search(query)

    # Concatenate the content of all retrieved documents into a single string
    full_content = ' '.join(doc.page_content for doc in docs)

    return full_content


# Function to create the system message for RAG (Retrieve and Generate)
def get_system_message_rag(content):
    return f"""You are a grade school math teacher that is attempting to help tutor kids on mathematical problems.

    Generate your response by following the steps below:
    1. Recursively break down the question into smaller questions.
    2. For each question/directive:
        2a. Select the most relevant information from the context in light of the conversation history.
    3. Generate a draft response using selected information.
    4. Remove duplicate content from draft response.
    5. Generate your final response after adjusting it to increase accuracy and relevance.
    6. Do not try to summarise the answers, explain it properly.
    6. Only show your final response! 

    Constraints:
    1. DO NOT PROVIDE ANY EXPLANATION OR DETAILS OR MENTION THAT YOU WERE GIVEN CONTEXT.
    2. Don't mention that you are not able to find the answer in the provided context.
    3. DO NOT USE ANY NAMES GIVEN IN THE CONTENT IN YOUR RESPONSE.

    CONTENT:
    {content}
    """


# Function to create the user query prompt
def get_ques_response_prompt(question):
    return f"""
    ==============================================================
    Based on the above context, please provide the answer to the following question:
    {question}
    """


# Function to generate RAG response using Ollama
def generate_rag_response(content, question):
    try:
        # Initialize the Ollama client with the specified host
        client = Client(host='http://localhost:11434')

        # Send a chat request to the Ollama model with the system message and user question
        stream = client.chat(model='llama3', messages=[
            {"role": "system", "content": get_system_message_rag(content)},
            {"role": "user", "content": get_ques_response_prompt(question)}
        ], stream=True)

        # Collect the response chunks as they arrive
        full_answer = ''
        for chunk in stream:
            full_answer += chunk['message']['content']

        return full_answer

    except Exception as e:
        # Handle connection errors
        print(f"Error connecting to Ollama server: {e}")
        return "Error: Unable to generate response due to connection issues."