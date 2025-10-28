import json
from chroma_db import chroma_script
import asyncio
import time


from bs4 import BeautifulSoup
import json, re

CITE_PATTERN = re.compile(r"\[cite:.*?\]")

def strip_citations(text: str) -> str:
    return CITE_PATTERN.sub("", text).strip()

def parse_kin(text: str):
    # Use XML parser to preserve tag names and whitespace handling
    soup = BeautifulSoup(text, "html.parser")

    short_el = soup.find("short_answer")
    detailed_el = soup.find("detailed_answer")
    refs_el = soup.find("guideline_references")

    result = {
        "short_answer": strip_citations(short_el.get_text(" ", strip=True)) if short_el else None,
        "detailed_answer": strip_citations(detailed_el.get_text(" ", strip=True)) if detailed_el else None,
        "guideline_references": []
    }

    if refs_el:
        inner = refs_el.get_text().strip()

        # First try: treat inner text as a comma-separated sequence of JSON objects -> wrap with []
        try:
            refs = json.loads(f"[{inner}]")
        except json.JSONDecodeError:
            # Fallback: extract each {...} block and parse individually
            refs = []
            for block in re.findall(r"\{.*?\}", inner, flags=re.S):
                try:
                    refs.append(json.loads(block))
                except json.JSONDecodeError:
                    # Soft-clean smart quotes, keep raw on failure
                    cleaned = (block
                               .replace("“", '"').replace("”", '"')
                               .replace("’", "'").replace("‘", "'"))
                    try:
                        refs.append(json.loads(cleaned))
                    except json.JSONDecodeError:
                        refs.append({"raw": block})

        result["guideline_references"] = refs

    return result

# --- usage ---
    
    


start = time.time()

# result = asyncio.run(chroma_script.rag_from_json(
#     query="Tell me about Sarah Miller lab results and is it relate to any EASL guidelines?",
#     top_k=3
# ))
# print("RAG Result:", result)
# with open("example.txt", "w", encoding="utf-8") as f:
#     f.write(result)


with open("example.txt", "r", encoding="utf-8") as f:
        kin_text = f.read()
data = parse_kin(kin_text)
with open("data_parsed.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

end = time.time()
print(f"Execution time: {end - start:.4f} seconds")