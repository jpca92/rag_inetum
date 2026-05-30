from collections import deque
from urllib.parse import urljoin, urlparse

import requests
import trafilatura
from bs4 import BeautifulSoup

from app.config import settings
from app.scraping.cleaner import TextCleaner
from app.scraping.storage import write_jsonl


class WebsiteScraper:
    def __init__(
        self,
        start_url: str = settings.SCRAPER_START_URL,
        allowed_domain: str = settings.SCRAPER_ALLOWED_DOMAIN,
        max_pages: int = settings.SCRAPER_MAX_PAGES,
        timeout_seconds: int = settings.SCRAPER_TIMEOUT_SECONDS,
    ):
        self.start_url = start_url
        self.allowed_domain = allowed_domain
        self.max_pages = max_pages
        self.timeout_seconds = timeout_seconds
        self.cleaner = TextCleaner()

    def scrape(self) -> tuple[list[dict], list[dict]]:
        visited: set[str] = set()
        queue = deque([self.start_url])

        raw_pages: list[dict] = []
        clean_documents: list[dict] = []

        while queue and len(visited) < self.max_pages:
            url = queue.popleft()

            if url in visited or not self._is_allowed_url(url):
                continue

            try:
                response = requests.get(
                    url,
                    timeout=self.timeout_seconds,
                    headers={"User-Agent": "Mozilla/5.0 RAG Technical Test Bot"},
                )
                response.raise_for_status()
            except requests.RequestException:
                visited.add(url)
                continue

            html = response.text
            visited.add(url)

            title = self._extract_title(html)

            extracted_text = trafilatura.extract(html)
            text = extracted_text or self._extract_text_with_bs4(html)

            clean_text = self.cleaner.clean(text)

            raw_pages.append(
                {
                    "url": url,
                    "title": title,
                    "html": html,
                }
            )

            if len(clean_text) > 200:
                clean_documents.append(
                    {
                        "url": url,
                        "title": title,
                        "content": clean_text,
                    }
                )

            for link in self._extract_links(html, url):
                if link not in visited and self._is_allowed_url(link):
                    queue.append(link)

        write_jsonl(settings.RAW_DATA_PATH, raw_pages)
        write_jsonl(settings.CLEAN_DATA_PATH, clean_documents)

        return raw_pages, clean_documents

    def _is_allowed_url(self, url: str) -> bool:
        parsed = urlparse(url)

        return (
            parsed.scheme in {"http", "https"}
            and parsed.netloc == self.allowed_domain
        )

    def _extract_title(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        if soup.title and soup.title.string:
            return soup.title.string.strip()

        h1 = soup.find("h1")

        if h1:
            return h1.get_text(strip=True)

        return "Sin título"

    def _extract_text_with_bs4(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        return soup.get_text(" ", strip=True)

    def _extract_links(self, html: str, base_url: str) -> set[str]:
        soup = BeautifulSoup(html, "html.parser")
        links = set()

        for tag in soup.find_all("a", href=True):
            href = tag["href"].split("#")[0].strip()

            if not href:
                continue

            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            clean_url = parsed._replace(query="").geturl()

            links.add(clean_url)

        return links