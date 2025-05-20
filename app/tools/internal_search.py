from app.vector_store.embeddings import search_similar

def internal_search(query):
    results = search_similar(query)
    return results["documents"]