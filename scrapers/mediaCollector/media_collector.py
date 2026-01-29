import argparse
import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class MediaCollector:
    """A lightweight tool to discover and optionally download media assets from a web page."""

    MEDIA_TAGS = [
        ("img", "src", "image"),
        ("img", "data-src", "image"),
        ("img", "data-lazy", "image"),
        ("source", "src", "mixed"),
        ("video", "src", "video"),
        ("video", "poster", "image"),
        ("audio", "src", "audio"),
        ("iframe", "src", "iframe"),
    ]

    STYLE_URL_PATTERN = re.compile(r"url\(['\"]?([^'\")]+)['\"]?\)", re.IGNORECASE)

    def __init__(self, session: Optional[requests.Session] = None, max_workers: int = 4, timeout: int = 15):
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        self.max_workers = max_workers
        self.timeout = timeout

    def _normalize_url(self, base: str, link: str) -> Optional[str]:
        if not link:
            return None
        absolute = urljoin(base, link)
        cleaned = absolute.split("#")[0]
        parsed = urlparse(cleaned)
        if not parsed.scheme or not parsed.netloc:
            return None
        return cleaned

    def _fetch_soup(self, url: str) -> BeautifulSoup:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _extract_inline_styles(self, tag, base_url: str) -> List[str]:
        results = []
        style = tag.get("style") or ""
        for match in self.STYLE_URL_PATTERN.findall(style):
            normalized = self._normalize_url(base_url, match)
            if normalized:
                results.append(normalized)
        return results

    def extract_media(self, soup: BeautifulSoup, page_url: str) -> List[dict]:
        media = []
        seen_urls = set()

        def register(url: str, media_type: str, context: str):
            normalized = self._normalize_url(page_url, url)
            if normalized and normalized not in seen_urls:
                seen_urls.add(normalized)
                media.append({"url": normalized, "type": media_type, "context": context, "source_page": page_url})

        for tag_name, attr, media_type in self.MEDIA_TAGS:
            for tag in soup.find_all(tag_name):
                value = tag.get(attr)
                if value:
                    register(value, media_type, f"<{tag_name} {attr}>")
                register_tag_set = tag.get("srcset")
                if attr == "src" and register_tag_set:
                    for chunk in register_tag_set.split(","):
                        candidate = chunk.strip().split(" ")[0]
                        if candidate:
                            register(candidate, media_type, "<img srcset>")
                for style_url in self._extract_inline_styles(tag, page_url):
                    register(style_url, "style-background", f"<{tag_name} style>")

        # Additional style-only searches
        for tag in soup.select("[style]"):
            for style_url in self._extract_inline_styles(tag, page_url):
                register(style_url, "style-background", f"<{tag.name} style>")

        return media

    def extract_links(self, soup: BeautifulSoup, page_url: str) -> List[str]:
        links = []
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            if href.lower().startswith("mailto:") or href.lower().startswith("javascript:"):
                continue
            normalized = self._normalize_url(page_url, href)
            if normalized:
                links.append(normalized)
        return links

    def collect(
        self,
        start_url: str,
        depth: int = 0,
        follow_links: bool = False,
        limit_pages: Optional[int] = None,
    ) -> List[dict]:
        queue = [(start_url, 0)]
        visited = set()
        collected = []
        start_domain = urlparse(start_url).netloc

        while queue:
            url, current_depth = queue.pop(0)
            if limit_pages and len(visited) >= limit_pages:
                break
            if url in visited:
                continue
            try:
                soup = self._fetch_soup(url)
            except Exception as exc:
                logging.warning("Failed to read %s: %s", url, exc)
                visited.add(url)
                continue

            visited.add(url)
            page_media = self.extract_media(soup, url)
            logging.info("Found %d media items on %s", len(page_media), url)
            collected.extend(page_media)

            if follow_links and current_depth < depth:
                for link in self.extract_links(soup, url):
                    link_domain = urlparse(link).netloc
                    if link_domain == start_domain and link not in visited:
                        queue.append((link, current_depth + 1))

        return collected

    def download_media(self, media_items: List[dict], output_dir: str) -> List[dict]:
        os.makedirs(output_dir, exist_ok=True)

        def worker(item):
            url = item["url"]
            filename = os.path.basename(urlparse(url).path) or "media"
            filename = re.sub(r"[^\w\.-]", "_", filename)
            path = os.path.join(output_dir, filename)
            if os.path.exists(path):
                return {"url": url, "path": path, "status": "skipped", "reason": "already exists"}

            try:
                response = self.session.get(url, timeout=self.timeout, stream=True)
                response.raise_for_status()
                with open(path, "wb") as handle:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            handle.write(chunk)
                return {"url": url, "path": path, "status": "saved"}
            except Exception as exc:
                return {"url": url, "status": "failed", "reason": str(exc)}

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_item = {executor.submit(worker, item): item for item in media_items}
            for future in as_completed(future_to_item):
                results.append(future.result())

        return results


def main():
    parser = argparse.ArgumentParser(description="Collect media assets (images, videos, audio) from one or more web pages.")
    parser.add_argument("--url", "-u", required=True, help="Starting URL to scrape.")
    parser.add_argument("--depth", "-d", type=int, default=0, help="Number of link-hops to follow (same domain only).")
    parser.add_argument("--follow-links", action="store_true", help="Follow internal links up to --depth.")
    parser.add_argument("--limit-pages", type=int, default=None, help="Maximum number of pages to visit (default: no limit).")
    parser.add_argument("--download", "-o", action="store_true", help="Download the discovered media files.")
    parser.add_argument("--output-dir", "-p", default="media_archive", help="Directory for downloads.")
    parser.add_argument("--manifest", "-m", default="media_manifest.json", help="File name to store media metadata.")
    parser.add_argument("--max-workers", type=int, default=4, help="Number of concurrent downloads.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    collector = MediaCollector(max_workers=args.max_workers)
    media = collector.collect(
        start_url=args.url,
        depth=args.depth,
        follow_links=args.follow_links,
        limit_pages=args.limit_pages,
    )

    manifest = {
        "start_url": args.url,
        "collected_at": datetime.utcnow().isoformat() + "Z",
        "total_media": len(media),
        "media": media,
    }

    with open(args.manifest, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    logging.info("Saved manifest to %s", args.manifest)

    if args.download and media:
        results = collector.download_media(media, args.output_dir)
        summary = {
            "downloaded": sum(1 for r in results if r["status"] == "saved"),
            "skipped": sum(1 for r in results if r["status"] == "skipped"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
        }
        summary_path = os.path.join(args.output_dir, "download_summary.json")
        with open(summary_path, "w", encoding="utf-8") as fh:
            json.dump({"summary": summary, "results": results}, fh, indent=2)
        logging.info("Download summary saved to %s", summary_path)

    print(f"\nCollected {len(media)} media items from {args.url}")


if __name__ == "__main__":
    main()
