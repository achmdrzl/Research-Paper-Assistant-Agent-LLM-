# from app.tools import upload_pdf, internal_search, compare_papers
# from app.tools import web_search

# Rule-based agent (without LangChain)
# def run_agent(prompt):
#     prompt = prompt.lower()
#     if "upload" in prompt:
#         return "Please upload a PDF using /upload endpoint."
#     elif "recent" in prompt or "find" in prompt or "search" in prompt:
#         return web_search.search_arxiv(prompt)
#     # elif any(word in prompt for word in ["find", "search", "semantic", "recent", "paper"]):
#     #     return web_search.search_semanticscholar(prompt)
#     elif "compare" in prompt:
#         paper1 = {"title": "Paper A", "abstract": "This is abstract A."}
#         paper2 = {"title": "Paper B", "abstract": "This is abstract B."}
#         return compare_papers.compare_papers(paper1, paper2)
#     else:
#         return "Sorry, I didn't understand the instruction."


# def run_agent(prompt):
#     prompt = prompt.lower()

#     if "compare" in prompt:
#         paper1 = {"title": "Paper A", "abstract": "This is abstract A."}
#         paper2 = {"title": "Paper B", "abstract": "This is abstract B."}
#         return compare_papers.compare_papers(paper1, paper2)

#     elif "upload" in prompt:
#         return "Please upload a PDF using /upload endpoint."

#     elif "recent" in prompt or "find" in prompt or "search" in prompt:
#         return web_search.search_arxiv(prompt)

#     else:
#         return "Sorry, I didn't understand the instruction."


# temp memory
# last_uploaded_paper = None
# last_web_paper = None

# def run_agent(prompt):
#     global last_uploaded_paper, last_web_paper

#     prompt = prompt.lower()

#     if "compare" in prompt:
#         if last_uploaded_paper and last_web_paper:
#             return compare_papers.compare_papers(last_uploaded_paper, last_web_paper)
#         else:
#             return "Please upload and search papers first."

#     elif "upload" in prompt:
#         return "Please upload a PDF using /upload endpoint."

#     elif "recent" in prompt or "find" in prompt or "search" in prompt:
#         papers = web_search.search_arxiv(prompt)
#         if papers:
#             title, abstract, _ = papers[0]
#             last_web_paper = {"title": title, "abstract": abstract}
#         return papers

#     else:
#         return "Sorry, I didn't understand the instruction."

# app/agent.py

from app.tools import upload_pdf, internal_search, web_search, compare_papers
from app.database.db import SessionLocal
from app.database.models import Paper

last_web_paper = None  # Global container for arxiv search results
last_search_results = []

def run_agent(prompt):
    global last_web_paper, last_search_results

    prompt_lower = prompt.lower()

    if "upload" in prompt_lower:
        return "Please upload the PDF file via the upload button."
    
    elif any(keyword in prompt.lower() for keyword in ["recent", "find", "search" , "look"]):
        papers = web_search.search_arxiv(prompt)
        if papers:
            title, abstract, _ = papers[0]
            last_web_paper = {"title": title, "abstract": abstract}
        return papers

    elif "internal" in prompt_lower:
        last_search_results = internal_search.internal_search(prompt)
        return last_search_results

    elif any(keyword in prompt.lower() for keyword in ["compare"]):
        return run_compare()

    else:
        return "Command not recognized. Use 'find', 'compare', or 'upload'."

def run_compare():
    global last_web_paper

    db = SessionLocal()
    paper_uploaded = db.query(Paper).filter(Paper.source == "internal_upload").order_by(Paper.created_at.desc()).first()

    if not paper_uploaded:
        return "❌ No paper uploads were found."

    if not last_web_paper:
        return "❌ There are no web search results to compare."

    paper1 = last_web_paper
    paper2 = {"title": paper_uploaded.title, "abstract": paper_uploaded.abstract}

    return compare_papers.compare_papers(paper1, paper2)
