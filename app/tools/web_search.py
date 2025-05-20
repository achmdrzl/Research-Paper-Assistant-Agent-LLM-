# import requests
# from app.database.db import SessionLocal
# from app.database.models import Paper
# from app.vector_store.embeddings import embed_and_store


# def search_arxiv(query):
#     url = f"http://export.arxiv.org/api/query?search_query={query}&max_results=3"
#     res = requests.get(url)
#     # Extract title and summary (abstract) using regex or XML parser
#     # For brevity, this part is simplified
#     results = [("Sample Title", "Sample Abstract")]
    
#     db = SessionLocal()
#     for title, abstract in results:
#         paper = Paper(title=title, abstract=abstract, source="web_search")
#         db.add(paper)
#         db.commit()
#         db.refresh(paper)
#         embed_and_store(paper.id, title, abstract, {"source": "web_search"})
#     return results


# import requests
# import xml.etree.ElementTree as ET
# from app.database.db import SessionLocal
# from app.database.models import Paper
# from app.vector_store.embeddings import embed_and_store

# def search_arxiv(query):
#     url = f"http://export.arxiv.org/api/query?search_query={query}&max_results=3"
#     res = requests.get(url)

#     if res.status_code != 200:
#         return [("Error", "Failed to fetch arXiv data")]

#     # Parse XML response
#     root = ET.fromstring(res.content)
#     ns = {'atom': 'http://www.w3.org/2005/Atom'}

#     entries = root.findall("atom:entry", ns)
#     results = []

#     for entry in entries:
#         title_elem = entry.find("atom:title", ns)
#         summary_elem = entry.find("atom:summary", ns)
#         if title_elem is not None and summary_elem is not None:
#             title = title_elem.text.strip().replace("\n", " ")
#             summary = summary_elem.text.strip().replace("\n", " ")
#             results.append((title, summary))

#     # Save to DB and embed
#     db = SessionLocal()
#     for title, abstract in results:
#         paper = Paper(title=title, abstract=abstract, source="web_search")
#         db.add(paper)
#         db.commit()
#         db.refresh(paper)
#         embed_and_store(paper.id, title, abstract, {"source": "web_search"})

#     return results


import requests
import xml.etree.ElementTree as ET
from app.database.db import SessionLocal
from app.database.models import Paper
from app.vector_store.embeddings import embed_and_store

def search_arxiv(query):
    url = f"http://export.arxiv.org/api/query?search_query={query}&max_results=3"
    res = requests.get(url)

    if res.status_code != 200:
        return [("Error", "Failed to fetch from arXiv")]

    # Parse XML
    root = ET.fromstring(res.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    entries = root.findall("atom:entry", ns)
    results = []

    for entry in entries:
        title_elem = entry.find("atom:title", ns)
        summary_elem = entry.find("atom:summary", ns)
        id_elem = entry.find("atom:id", ns)

        if title_elem is not None and summary_elem is not None:
            title = title_elem.text.strip().replace("\n", " ")
            summary = summary_elem.text.strip().replace("\n", " ")
            link = id_elem.text.strip() if id_elem is not None else ""
            results.append((title, summary, link))

    # Save to DB and vector store
    db = SessionLocal()
    for title, abstract, link in results:
        paper = Paper(title=title, abstract=abstract, source="web_search")
        db.add(paper)
        db.commit()
        db.refresh(paper)
        embed_and_store(paper.id, title, abstract, {"source": "web_search", "link": link})

    return results


