import json
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import uuid

# Load the JSONL file
file_path = r'C:\Users\Lachlan Angelis\Documents\GitHub\MathBuddyAPI\traindata\labeled_train_data.jsonl'

# Read the JSONL file and parse its content
with open(file_path, 'r') as f:
    lines = f.readlines()

# Convert each line in the JSONL file into a dictionary
documents = [json.loads(line) for line in lines]

# Initialize ChromaDB client
print("Initializing ChromaDB client...")
client = chromadb.HttpClient(host='localhost', port=8000, settings=Settings(allow_reset=True))

# Reset the database
try:
    client.reset()  # Reset the database
    print("Database reset successful.")
except Exception as e:
    print(f"Error resetting the database: {e}")

# Create or connect to a collection named "my_collection"
print("Creating or connecting to collection 'my_collection'...")
collection = client.get_or_create_collection("my_collection")

# Initialize the sentence transformer model for generating embeddings
print("Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Prepare lists for document IDs, texts, embeddings, and metadata
print("Processing documents...")
for idx, doc in enumerate(documents):
    # Create a unique identifier for each document
    document_id = str(uuid.uuid4())
    document_text = f"Question: {doc['question']} Answer: {doc['answer']}"

    # Debug statements
    print(f"Processing document {idx + 1}/{len(documents)}")
    print(f"Document ID: {document_id}")
    print(f"Document text: {document_text}")

    # Generate embeddings for the document text
    document_embedding = embedding_model.encode(document_text).tolist()

    # Debug statement
    print(f"Generated embedding for document {document_id}: {document_embedding[:5]}... (truncated)")

    # Add the document to the collection with embeddings and metadata
    try:
        collection.add(
            ids=[document_id],
            embeddings=[document_embedding],
            metadatas=[{
                "text": document_text,
                "difficulty": doc["difficulty"],
                "operation": doc["operation"]
            }],
            documents=[document_text]
        )
        print(f"Document {document_id} added successfully.")
    except Exception as e:
        print(f"Error adding document {document_id}: {e}")

print("Documents inserted into ChromaDB.")
