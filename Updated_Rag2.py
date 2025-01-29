import subprocess
import json
from pathlib import Path
from typing import List
import numpy as np
from sklearn.preprocessing import normalize
import torch
from transformers import AutoTokenizer, AutoModel
import os
import pdfplumber
import faiss

# Silence Hugging Face symlink warning
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

# Load Q&A data from JSON
file_path = Path('qa_data.json')
with open(file_path, 'r') as file:
    qa_data = json.load(file)

documents = [
    {"question": entry["question"], "answer": entry["answer"]}
    for entry in qa_data['qa_data']
]
print(f"Loaded {len(documents)} Q&A pairs.")

# Chunk text into smaller parts (500 characters max, with overlap)
def chunk_text(text: str, max_length: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_length, len(text))
        chunks.append(text[start:end])
        start += max_length - overlap
    return chunks

document_chunks = []
for entry in documents:
    question_chunks = chunk_text(entry['question'])
    answer_chunks = chunk_text(entry['answer'])
    document_chunks.extend(question_chunks)
    document_chunks.extend(answer_chunks)
print(f"Created {len(document_chunks)} chunks from the Q&A data.")

# Extract text from PDF using pdfplumber
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Load the PDF file (update the file name here)
pdf_files = ['qa_data.pdf']  # Pointing to your specific PDF file
pdf_texts = [extract_text_from_pdf(pdf) for pdf in pdf_files]

# Add PDF texts to document chunks
for pdf_text in pdf_texts:
    pdf_chunks = chunk_text(pdf_text)
    document_chunks.extend(pdf_chunks)

# Initialize Hugging Face model and tokenizer for embeddings
model_name = 'bert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Generate embeddings for a given text
def generate_embedding(text: str) -> np.ndarray:
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)  # Average pooling
    return embeddings.squeeze().cpu().numpy()

# Generate embeddings for all document chunks
embeddings = []
for chunk in document_chunks:
    embedding = generate_embedding(chunk)
    embeddings.append(embedding)

# Normalize embeddings for similarity search
embeddings = normalize(embeddings)

# Create FAISS index
embedding_dim = len(embeddings[0])
index = faiss.IndexFlatL2(embedding_dim)
embedding_matrix = np.array(embeddings).astype(np.float32)
index.add(embedding_matrix)

# Function to send a query to Ollama model (Mistral)
def send_query_to_ollama(query: str) -> str:
    command = ["ollama", "run", "mistral", query]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running Ollama command: {e}")
        return "Error communicating with the model."

# Find most relevant document chunk using FAISS
def faiss_query(query: str, index: faiss.Index, document_chunks: List[str], k: int = 1) -> str:
    query_embedding = generate_embedding(query)
    query_embedding = np.array([query_embedding], dtype=np.float32)
    distances, indices = index.search(query_embedding, k)
    most_similar_idx = indices[0][0]
    return document_chunks[most_similar_idx], indices[0][0]

# Generate contextual answer using Ollama
def generate_contextual_answer(query: str, document_chunk: str, source_idx: int) -> str:
    context = f"Context: {document_chunk}\n\n"
    prompt = f"{context}Question: {query}\nAnswer:"
    response = send_query_to_ollama(prompt)
    return response, source_idx

# Example query
query = "Who painted the Mona Lisa?"
response, source_idx = faiss_query(query, index, document_chunks)

if response:
    final_response, source_idx = generate_contextual_answer(query, response, source_idx)
    print(f"Final Response: {final_response}")
else:
    print("No relevant information found.")
