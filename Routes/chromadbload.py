import json
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import uuid

# Load and parse the JSONL file containing the labeled training data
file_path = '../traindata/labeled_train_data.jsonl'

# Read the JSONL file and convert each line into a dictionary
with open(file_path, 'r') as f:
    lines = f.readlines()
documents = [json.loads(line) for line in lines]

# Initialize ChromaDB client for managing embeddings and document storage
client = chromadb.HttpClient(host='localhost', port=8000, settings=Settings(allow_reset=True))

# Reset the ChromaDB database (if allowed)
try:
    client.reset()  # Clears the database, useful for fresh setups
except Exception as e:
    print(f"Error resetting the database: {e}")

# Create or connect to a collection named "my_collection" in ChromaDB
collection = client.get_or_create_collection("my_collection")

# Initialize the sentence transformer model for generating embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Loop through the documents, generating embeddings and inserting them into the collection
for idx, doc in enumerate(documents):
    # Generate a unique ID for each document
    document_id = str(uuid.uuid4())
    document_text = f"Question: {doc['question']} Answer: {doc['answer']}"

    # Generate embeddings for the document text
    document_embedding = embedding_model.encode(document_text).tolist()

    # Add the document with embeddings and metadata to the collection
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
    except Exception as e:
        print(f"Error adding document {document_id}: {e}")

# Print completion message
print("Documents successfully inserted into ChromaDB.")
