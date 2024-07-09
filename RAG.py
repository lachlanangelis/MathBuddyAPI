import json
import chromadb
from chromadb.config import Settings

# Load the JSONL file
file_path = 'path/to/your/cleaned_train.jsonl'

with open(file_path, 'r') as f:
    lines = f.readlines()

# Parse the JSONL content
documents = [json.loads(line) for line in lines]

# Initialize ChromaDB client
client = chromadb.Client(Settings())

# Create or connect to a collection
collection = client.get_or_create_collection("documents")

# Insert documents from JSONL
for idx, doc in enumerate(documents):
    document = {
        "id": f"doc{idx}",  # Use the line number as a unique identifier
        "text": f"Question: {doc['question']} Answer: {doc['answer']}"
    }
    collection.add([document])

print("Documents inserted into ChromaDB.")
