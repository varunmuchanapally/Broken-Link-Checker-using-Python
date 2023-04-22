import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Define the domain URL
domain_url = 'https://aitoptools.com/'

# Set up a set of visited URLs and a list of URLs to visit
visited_urls = set()
urls_to_visit = [domain_url]

# Set up a list to store external links
external_links = []

# Define a function to extract external links from a page
def extract_external_links(url, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and 'http' in href and domain_url not in href:
            external_links.append(href)

# Start crawling the domain
while urls_to_visit:
    # Get the next URL to visit
    url = urls_to_visit.pop(0)

    # Skip URLs that have already been visited
    if url in visited_urls:
        continue

    # Send an HTTP request to the URL and get its HTML content
    response = requests.get(url)
    html_content = response.text

    # Extract external links from the page
    extract_external_links(url, html_content)

    # Mark the URL as visited
    visited_urls.add(url)

    # Find all internal links on the page and add them to the list of URLs to visit
    soup = BeautifulSoup(html_content, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and 'http' not in href:
            abs_url = urljoin(url, href)
            if abs_url.startswith(domain_url) and abs_url not in visited_urls and abs_url not in urls_to_visit:
                urls_to_visit.append(abs_url)

# Print the list of external links
print(external_links)
