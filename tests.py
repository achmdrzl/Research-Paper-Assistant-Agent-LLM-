from app.tools import web_search

if __name__ == "__main__":
    query = "fine-tuning transformers"
    print(f"🔍 Testing arXiv search with query: '{query}'")
    results = web_search.search_arxiv(query)

    if not results:
        print("❌ No results returned.")
    else:
        print(f"✅ {len(results)} results returned:")
        for i, (title, abstract, link) in enumerate(results, start=1):
            print(f"\n📄 Result {i}")
            print(f"Title   : {title}")
            print(f"Abstract: {abstract[:200]}...")
            print(f"Link    : {link}")
