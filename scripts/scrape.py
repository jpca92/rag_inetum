import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.scraping.scraper import WebsiteScraper


if __name__ == "__main__":
    raw_pages, clean_documents = WebsiteScraper().scrape()

    print(f"Raw pages: {len(raw_pages)}")
    print(f"Clean documents: {len(clean_documents)}")
