# Import necessary libraries and modules
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from ollama import Client

# Function to extract relevant context using ChromaDB
def extract_context(query):
    # Initialize ChromaDB client for similarity searches
    chroma_client = chromadb.HttpClient(host='localhost', port=8000, settings=Settings(allow_reset=True))

    # Use a pre-trained sentence transformer model for embeddings
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create a Chroma instance for interacting with the document collection
    db = Chroma(
        client=chroma_client,
        collection_name="my_collection",  # Collection in ChromaDB where documents are stored
        embedding_function=embedding_function,
    )

    # Perform a similarity search in the collection based on the query
    docs = db.similarity_search(query)

    # Concatenate the content of the retrieved documents into a single string
    full_content = ' '.join(doc.page_content for doc in docs)

    return full_content

# Function to create the system message for RAG (Retrieve and Generate) response
def get_system_message_rag(content):
    return f"""You are a grade school math teacher that is attempting to help tutor kids on mathematical problems.

    Generate your response by following the steps below:
    1. For each question/directive:
        1a. Select the most relevant information from the context.

    Constraints:
    1. DO NOT PROVIDE ANY EXPLANATION OR DETAILS OR MENTION THAT YOU WERE GIVEN CONTEXT.
    2. Don't mention that you are not able to find the answer in the provided context.
    3. DO NOT USE ANY NAMES GIVEN IN THE CONTENT IN YOUR RESPONSE.
    4. DO NOT REUSE ANY OF THE CONTEXT OF THE PREVIOUS QUESTIONS.
    5. DO NOT REUSE ANY OF THE PREVIOUS QUESTIONS.
    6. DO NOT ANSWER THE QUESTION.

    CONTENT:
    {content}
    """

# Function to create the user query prompt based on the question
def get_ques_response_prompt(question):
    return f"""
    ==============================================================
    Based on the above context, please provide the answer to the following question:
    {question}
    """

# Function to generate a RAG-based response using Ollama
def generate_rag_response(content, question):
    try:
        # Initialize the Ollama client for generating responses
        client = Client(host='http://localhost:11434')

        # Send the system message and user question to the model
        stream = client.chat(model='llama3', messages=[
            {"role": "system", "content": get_system_message_rag(content)},
            {"role": "user", "content": get_ques_response_prompt(question)}
        ], stream=True)

        # Collect and concatenate the response chunks as they arrive
        full_answer = ''
        for chunk in stream:
            full_answer += chunk['message']['content']

        return full_answer

    except Exception as e:
        # Handle connection errors gracefully
        print(f"Error connecting to Ollama server: {e}")
        return "Error: Unable to generate response due to connection issues."
