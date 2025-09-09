import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
from urllib.parse import urljoin, urlparse
import sys
import time
import random
import csv
from datetime import datetime, UTC
import os

SEARCH_STRINGS = {"10/15/24", "10/15/2024", "10/14/2024", "10/14/24"}
visited_pages = set()
results = []

def get_links_and_pdfs(page_url):
    try:
        resp = requests.get(page_url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching {page_url}: {e}")
        return [], []
    soup = BeautifulSoup(resp.content, "html.parser")
    subpages = set()
    pdfs = set()
    # Find the div and the table
    div = soup.find("div", class_="table-responsive")
    if not div:
        print(f"No <div class='table-responsive'> found in {page_url}")
        return [], []
    table = div.find("table", id="fileBrowsingTable")
    if not table:
        print(f"No <table id='fileBrowsingTable'> found in {page_url}")
        return [], []
    for link in table.find_all("a", href=True):
        href = link['href']
        url = urljoin(page_url, href)
        if url.endswith(".pdf"):
            pdfs.add(url)
        else:
            # Only crawl links within same domain
            if urlparse(url).netloc == urlparse(page_url).netloc:
                subpages.add(url)
    return list(subpages), list(pdfs)

def scan_pdf(pdf_url):
    print(f"Scanning PDF: {pdf_url}")
    try:
        resp = requests.get(pdf_url, timeout=15)
        resp.raise_for_status()
        with io.BytesIO(resp.content) as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                try:
                    page_text = page.extract_text() or ""
                    text += page_text
                except Exception:
                    continue
            preview = text[:200].replace('\n', ' ') if text else "[No text extracted]"
            # print(f"Text preview from {pdf_url}: {preview}")  # <-- Commented out as requested
            found = [s for s in SEARCH_STRINGS if s in text]
            return found
    except Exception as e:
        print(f"Error reading PDF {pdf_url}: {e}")
        return []

def crawl(page_url):
    if page_url in visited_pages:
        return
    visited_pages.add(page_url)
    print(f"Traversing page: {page_url}")
    subpages, pdfs = get_links_and_pdfs(page_url)
    for pdf_url in pdfs:
        found = scan_pdf(pdf_url)
        if found:
            results.append({
                "page_url": page_url,
                "pdf_url": pdf_url,
                "found_strings": ": ".join(found)  # Changed separator to colon
            })
        time.sleep(1.0 + random.uniform(0, 0.9))  # 1 second + variable tenths
    for subpage_url in subpages:
        time.sleep(1.0 + random.uniform(0, 0.9))  # 1 second + variable tenths
        crawl(subpage_url)

def print_table():
    if not results:
        print("No matching PDFs found.")
        return
    print(f"{'Page URL':<60} {'PDF URL':<60} {'Found Strings':<30}")
    print("-"*150)
    for r in results:
        print(f"{r['page_url']:<60} {r['pdf_url']:<60} {r['found_strings']:<30}")

def write_csv():
    # Only write CSV if there are results
    if not results:
        print("No matching PDFs found.")
        return
    # Use current working directory, and current UTC time
    now = datetime.now(UTC)
    filename = f"fcc_public_file_scan{now.strftime('%Y%m%d_%H%M')}.csv"
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, mode="w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Page URL", "PDF URL", "Found Strings"])
        for r in results:
            writer.writerow([r["page_url"], r["pdf_url"], r["found_strings"]])
    print(f"CSV saved to {filepath}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pdf_date_scanner.py <starting_url>")
        sys.exit(1)
    start_url = sys.argv[1]
    crawl(start_url)
    print_table()
    write_csv()