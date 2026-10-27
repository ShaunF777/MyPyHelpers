# You may need to install beautifulsoup4: pip install beautifulsoup4 html2text requests

import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin

# 1. Base URL of the Table of Contents you are viewing
base_url = "https://gcc.gnu.org/onlinedocs/cpp/index.html"
output_file = "full_c_preprocessor_docs.md"

# Configure the HTML-to-Markdown converter
converter = html2text.HTML2Text()
converter.ignore_links = False 

def get_subpage_links(toc_url):
    """
    Fetches the Table of Contents and extracts all subpage links.
    Think of BeautifulSoup as a robot that reads the HTML code and 
    organizes it into a searchable tree structure.
    """
    response = requests.get(toc_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    subpages = []
    
    # Find all anchor tags (<a>), which represent hyperlinks in HTML
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Skip purely on-page anchor links (e.g., "#SEC_Contents")
        if href.startswith('#'):
            continue
            
        # Combine the base URL with the relative link to get the full address
        full_url = urljoin(toc_url, href)
        
        # Only keep links that are part of this specific documentation folder
        # and avoid duplicates
        if full_url.startswith("https://gcc.gnu.org/onlinedocs/cpp/") and full_url not in subpages:
            subpages.append(full_url)
            
    return subpages

def build_single_markdown(toc_url, output_path):
    """Iterates through all subpages, converts them, and merges them."""
    # Step 1: Get the list of all URLs we need to visit
    links_to_scrape = get_subpage_links(toc_url)
    
    print(f"Found {len(links_to_scrape)} pages to combine. Starting...")
    
    # Step 2: Open our master .md file in 'append' or 'write' mode
    with open(output_path, "w", encoding="utf-8") as f:
        
        # Step 3: Loop through each link, fetch it, and translate it
        for index, link in enumerate(links_to_scrape):
            print(f"Processing {index + 1}/{len(links_to_scrape)}: {link}")
            
            try:
                page_response = requests.get(link)
                # Convert this specific page's HTML to Markdown
                md_text = converter.handle(page_response.text)
                
                # Write a divider, the source URL as a comment, and the content
                f.write(f"\n\n---\n<!-- Source: {link} -->\n\n")
                f.write(md_text)
            except Exception as e:
                print(f"Failed to process {link}: {e}")

    print(f"\nSuccess! All pages combined into {output_path}")

# Run the script
build_single_markdown(base_url, output_file)
