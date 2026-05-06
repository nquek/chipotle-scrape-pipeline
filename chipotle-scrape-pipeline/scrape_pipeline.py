import os
import re
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv("FIRECRAWL_API_KEY")
if not api_key:
    raise RuntimeError("FIRECRAWL_API_KEY is not set")

# --- Step 01: Search + scrape with Firecrawl ---

response = requests.post(
    "https://api.firecrawl.dev/v2/search",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "query": "Chipotle investor relations press releases",
        "limit": 5,
        "scrapeOptions": {"formats": ["markdown"]},
    },
)

print("Status:", response.status_code, "| Keys:", list(response.json().keys()))
results = response.json()["web"]
print(f"Firecrawl returned {len(results)} results")

# --- Step 02: Save each result as a markdown file ---

output_dir = Path("knowledge/raw")
output_dir.mkdir(parents=True, exist_ok=True)

date_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")

for i, r in enumerate(results, start=1):
    title = r.get("title") or re.sub(r"https?://", "", r.get("url", "unknown"))
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").lower()[:100]
    body = r.get("markdown") or "_No markdown content returned for this page._"
    content = (
        f"---\n"
        f"title: {title}\n"
        f"url: {r.get('url', '')}\n"
        f"saved_at: {datetime.now(timezone.utc).isoformat()}\n"
        f"---\n\n"
        + body
    )
    path = output_dir / f"{date_prefix}-{i:02d}-{slug}.md"
    path.write_text(content)
    print(f"  - {title}")
    print(f"    {r.get('url')}")
    print(f"    saved -> {path}")
