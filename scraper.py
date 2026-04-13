import asyncio
import os
import re
import sys
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler
from config import URL, MAX_PAGES, PRIORITY_PAGES

os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


async def _scrape(url):
    base_domain = urlparse(url).netloc
    visited = set()
    to_visit = [url] + [p.rstrip("/") for p in PRIORITY_PAGES]
    all_text = []

    async with AsyncWebCrawler() as crawler:
        while to_visit and len(visited) < MAX_PAGES:
            current = to_visit.pop(0)

            if current in visited:
                continue
            visited.add(current)

            print(f"  [{len(visited)}/{MAX_PAGES}] Scraping: {current}")

            try:
                result = await crawler.arun(url=current)
            except Exception as e:
                print(f"  Failed: {e}")
                continue

            if result.markdown:
                all_text.append(result.markdown)

            skip_extensions = (".css", ".js", ".ico", ".png", ".jpg", ".jpeg",
                               ".gif", ".svg", ".webp", ".pdf", ".zip", ".xml")
            skip_paths = ("/feed", "/comments", "/wp-json", "/wp-admin",
                          "/wp-login", "/wp-content", "/wp-includes",
                          "/xmlrpc", "/trackback", "/embed")

            if result.html:
                links = re.findall(r'href=["\']([^"\']+)', result.html)
                for link in links:
                    full_url = urljoin(current, link)
                    full_url = full_url.split("#")[0].split("?")[0].rstrip("/")
                    parsed = urlparse(full_url)
                    path = parsed.path.lower()
                    if (parsed.netloc == base_domain
                            and full_url not in visited
                            and not path.endswith(skip_extensions)
                            and not any(skip in path for skip in skip_paths)):
                        to_visit.append(full_url)

    print(f"  Scraped {len(visited)} pages")
    return "\n\n".join(all_text)


def scrape(url):
    return asyncio.run(_scrape(url))


if __name__ == "__main__":
    text = scrape(URL)
    print(text[:2000])
    print(f"\n--- Total length: {len(text)} characters ---")
