import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
import concurrent.futures
import json
import os

class NudogramScraper:
    def __init__(self, base_url, max_workers=5):
        """
        Initialize the scraper for Nudogram model pages

        Args:
            base_url: Base URL like 'https://nudogram-com.zproxy.org/models/oheytherehello/'
            max_workers: Number of concurrent requests
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.max_workers = max_workers
        self.found_pages = []

    def check_page_exists(self, page_num):
        """Check if a specific page exists and is accessible"""
        url = f"{self.base_url}/{page_num}"
        try:
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                # Additional check: page should contain some content
                soup = BeautifulSoup(response.content, 'html.parser')
                if soup.find('body'):
                    return True, url, response
            elif response.status_code == 404:
                return False, url, None

        except requests.RequestException as e:
            print(f"Error checking page {page_num}: {e}")

        return False, url, None

    def find_max_page_binary(self, max_attempt=10000):
        """
        Use binary search to find the maximum existing page number
        """
        low = 0
        high = max_attempt

        print(f"Searching for max page (binary search up to {max_attempt})...")

        while low <= high:
            mid = (low + high) // 2

            exists, url, _ = self.check_page_exists(mid)

            if exists:
                # Check next page to see if we should go higher
                next_exists, _, _ = self.check_page_exists(mid + 1)
                if not next_exists:
                    return mid  # Found max page
                else:
                    low = mid + 1
            else:
                high = mid - 1

            time.sleep(0.1)  # Small delay to be polite

        return high

    def find_max_page_linear(self, start=0, step=10, timeout=30):
        """
        Use linear probing to find pages with step size
        """
        print(f"Starting linear search from page {start}...")

        current_page = start
        found_pages = []
        start_time = time.time()

        while time.time() - start_time < timeout:
            exists, url, response = self.check_page_exists(current_page)

            if exists:
                found_pages.append(current_page)
                print(f"✓ Found page {current_page}")
                current_page += 1
            else:
                # Try skipping ahead
                skip_exists, skip_url, _ = self.check_page_exists(current_page + step)
                if skip_exists:
                    current_page += step
                    continue
                else:
                    # Maybe we found the end, check backwards
                    for i in range(1, step):
                        check_page = current_page - i
                        if check_page not in found_pages:
                            exists, _, _ = self.check_page_exists(check_page)
                            if exists:
                                current_page = check_page + 1
                                break
                    else:
                        # No more pages found
                        break

            time.sleep(0.2)

        return found_pages

    def scrape_page_content(self, url, response):
        """Extract content from a page"""
        soup = BeautifulSoup(response.content, 'html.parser')

        page_data = {
            'url': url,
            'title': soup.title.string if soup.title else 'No title',
            'images': [],
            'links': [],
            'text_content': soup.get_text()[:500] + '...' if soup.get_text() else 'No content'
        }

        # Find all images
        for img in soup.find_all('img', src=True):
            img_url = urljoin(url, img['src'])
            page_data['images'].append({
                'src': img_url,
                'alt': img.get('alt', ''),
                'class': img.get('class', [])
            })

        # Find all links
        for link in soup.find_all('a', href=True):
            href = urljoin(url, link['href'])
            page_data['links'].append({
                'url': href,
                'text': link.get_text(strip=True),
                'title': link.get('title', '')
            })

        return page_data

    def scrape_range(self, start_page, end_page):
        """Scrape a range of pages"""
        results = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create futures for all pages in range
            future_to_page = {}
            for page_num in range(start_page, end_page + 1):
                future = executor.submit(self.check_page_exists, page_num)
                future_to_page[future] = page_num

            # Process completed futures
            for future in concurrent.futures.as_completed(future_to_page):
                page_num = future_to_page[future]
                try:
                    exists, url, response = future.result()
                    if exists:
                        page_data = self.scrape_page_content(url, response)
                        results[page_num] = page_data
                        print(f"Scraped page {page_num}")
                except Exception as e:
                    print(f"Error processing page {page_num}: {e}")

        return results

    def find_all_pages(self, method='binary', **kwargs):
        """Find all existing pages using specified method"""
        if method == 'binary':
            max_page = self.find_max_page_binary(**kwargs)
            return list(range(0, max_page + 1))
        elif method == 'linear':
            return self.find_max_page_linear(**kwargs)
        else:
            raise ValueError("Method must be 'binary' or 'linear'")

    def save_results(self, results, output_dir='scraped_results'):
        """Save scraped results to files"""
        os.makedirs(output_dir, exist_ok=True)

        # Save summary
        summary = {
            'base_url': self.base_url,
            'total_pages': len(results),
            'pages': list(results.keys()),
            'timestamp': time.time()
        }

        with open(f'{output_dir}/summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        # Save individual page data
        for page_num, data in results.items():
            with open(f'{output_dir}/page_{page_num}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        # Save URLs to text file
        with open(f'{output_dir}/urls.txt', 'w', encoding='utf-8') as f:
            for page_num in sorted(results.keys()):
                f.write(f"{self.base_url}/{page_num}\n")

        print(f"Results saved to '{output_dir}' directory")

    def get_sitemap(self, pages):
        """Generate a sitemap of found pages"""
        print("\n" + "="*50)
        print("SITEMAP")
        print("="*50)

        for page in sorted(pages):
            print(f"Page {page}: {self.base_url}/{page}")

        print(f"\nTotal pages found: {len(pages)}")
        print("="*50)

def main():
    # Configuration
    BASE_URL = "https://nudogram-com.zproxy.org/models/oheytherehello"

    print("Nudogram Model Page Scraper")
    print("="*50)
    print(f"Target: {BASE_URL}")
    print("="*50)

    # Initialize scraper
    scraper = NudogramScraper(BASE_URL, max_workers=3)

    # Choose method
    print("\nChoose scanning method:")
    print("1. Binary Search (fastest)")
    print("2. Linear Scan (thorough)")
    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        # Binary search for max page
        try:
            max_page = int(input("Enter max page to search up to (default: 1000): ") or "1000")
        except:
            max_page = 1000

        print(f"\nPerforming binary search up to page {max_page}...")
        pages = scraper.find_all_pages('binary', max_attempt=max_page)

    else:
        # Linear scan
        print("\nPerforming linear scan...")
        try:
            timeout = int(input("Enter timeout in seconds (default: 30): ") or "30")
        except:
            timeout = 30

        pages = scraper.find_all_pages('linear', timeout=timeout)

    # Display results
    if pages:
        scraper.get_sitemap(pages)

        # Ask if user wants to scrape content
        scrape_content = input("\nScrape content from found pages? (y/n): ").lower().strip()

        if scrape_content.startswith('y'):
            print("\nScraping page content...")
            results = scraper.scrape_range(min(pages), max(pages))

            # Save results
            save = input("\nSave results to files? (y/n): ").lower().strip()
            if save.startswith('y'):
                scraper.save_results(results)
                print(f"\nScraped {len(results)} pages successfully!")
        else:
            print("\nURL list generated. You can use these URLs manually.")

    else:
        print("\nNo pages found. The site structure might have changed or requires authentication.")

if __name__ == "__main__":
    main()