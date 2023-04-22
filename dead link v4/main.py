import requests
from bs4 import BeautifulSoup

website_url = "https://aitoptools.com/" # Replace with the URL of the website you want to check
visited_urls = set()
broken_links = set()

def check_link(url):
    try:
        response = requests.get(url)
        if response.status_code >= 400:
            print(f"{url} is broken ({response.status_code})")
            broken_links.add(url)
    except requests.exceptions.RequestException as e:
        print(f"{url} is broken ({e})")
        broken_links.add(url)

def crawl(url):
    if url in visited_urls:
        return
    visited_urls.add(url)
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(f"{url} is broken ({e})")
        broken_links.add(url)
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href is None:
            continue
        if href.startswith('#'):
            continue
        if href.startswith('mailto:'):
            continue
        if ':' in href:
            continue
        if href.startswith('//'):
            href = f"https:{href}"
        elif href.startswith('/'):
            href = f"{website_url}{href}"
        elif not href.startswith('http'):
            href = f"{website_url}/{href}"
        check_link(href)
        crawl(href)

if __name__ == '__main__':
    crawl(website_url)
    print(f"Found {len(broken_links)} broken links:")
    for link in broken_links:
        print(link)
