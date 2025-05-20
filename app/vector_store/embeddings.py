from chromadb import Client
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
client = Client()
collection = client.get_or_create_collection(name="papers")

def get_embedding(text):
    return model.encode([text])[0]

def embed_and_store(doc_id, title, abstract, metadata):
    embedding = get_embedding(f"{title} {abstract}")
    collection.add(
        documents=[f"{title} {abstract}"],
        embeddings=[embedding],
        metadatas=[metadata],
        ids=[str(doc_id)]
    )

def search_similar(query):
    embedding = get_embedding(query)
    return collection.query(query_embeddings=[embedding], n_results=5)