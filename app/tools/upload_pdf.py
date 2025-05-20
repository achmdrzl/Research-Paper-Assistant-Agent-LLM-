import pdfplumber
from app.database.db import SessionLocal
from app.database.models import Paper
from app.vector_store.embeddings import embed_and_store
import re
import wordninja


def clean_and_split(text):
    """Clean up and break long text into lines"""
    return [line.strip() for line in text.splitlines() if line.strip()]

def smart_split_words(text):
    """Split text without spaces using wordninja"""
    if len(text.split()) == 1:  # only one token, may not have been split
        return wordninja.split(text)
    return text.split()

def truncate(text, max_words=100):
    """Cut too long text (e.g. abstract)"""
    words = smart_split_words(text)
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

# --- Method 1: Positional Heuristics ---
def extract_by_position(lines):
    title_lines = []
    abstract_lines = []
    abstract_found = False

    for i, line in enumerate(lines):
        l = line.strip()

        if not abstract_found and re.match(r'abstract', l, re.IGNORECASE):
            abstract_found = True
            continue

        if abstract_found:
            if re.match(r'(keywords|introduction|1\.|background)', l, re.IGNORECASE):
                break
            abstract_lines.append(l)
        elif i <= 2:
            title_lines.append(l)

    title = " ".join(title_lines).strip()
    abstract = " ".join(abstract_lines).strip()
    return title, abstract

# --- Method 2: Direct Regex ---
def extract_by_regex(text):
    title_match = re.search(r"^(.*?)\babstract\b", text, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else "Unknown Title"

    abstract_match = re.search(
        r"\babstract\b\s*[:\-]?\s*(.+?)(?=(\bkeywords\b|\bintroduction\b|1\.|\n\n))",
        text, re.IGNORECASE | re.DOTALL
    )
    abstract = abstract_match.group(1).strip() if abstract_match else "No abstract found."
    return title, abstract

# --- Method 3: Multilingual Semantic Detection ---
def extract_semantic(text):
    variants = ['abstract', 'abstrak', 'résumé', 'resumen', 'مُلخّص', '摘要']
    for variant in variants:
        pattern = rf"{variant}\s*[:\-]?\s*(.+?)(?=(keywords|introduction|1\.|methods|\n\n))"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            abstract = match.group(1).strip()
            return "Unknown Title", abstract
    return "Unknown Title", "No abstract found."

# --- Main Functions ---
def extract_metadata(text):
    lines = clean_and_split(text)
    full_text = "\n".join(lines)

    if len(lines) < 5:
        title, abstract = extract_by_regex(full_text)
    elif 'abstract' in full_text.lower():
        title, abstract = extract_by_position(lines)
    else:
        title, abstract = extract_semantic(full_text)

    # Normalize the output (including wordninja if necessary)
    title_clean = " ".join(smart_split_words(title))
    abstract_clean = truncate(abstract, max_words=120)
    return title_clean.strip(), abstract_clean.strip()

def upload_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        first_page = pdf.pages[0].extract_text()

    if not first_page:
        return {"error": "PDF has no extractable text."}

    title, abstract = extract_metadata(first_page)
    db = SessionLocal()
    new_paper = Paper(title=title, abstract=abstract, source="internal_upload")
    db.add(new_paper)
    db.commit()
    db.refresh(new_paper)
    embed_and_store(new_paper.id, title, abstract, {"source": "internal_upload"})
    return {"id": new_paper.id, "title": title, "abstract": abstract}
