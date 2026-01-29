import requests
import re
import json
import csv
import os
import time
import concurrent.futures
from datetime import datetime
from urllib.parse import urljoin, urlparse
import random

class PimpBunnyUsernameScraper:
    """Lightweight scraper to extract usernames from PimpBunny URLs"""

    def __init__(self):
        self.session = requests.Session()
        self.setup_headers()
        self.usernames = set()  # Use set to avoid duplicates
        self.profile_urls = []

    def setup_headers(self):
        """Setup headers to mimic a real browser"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.800',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        })

    def extract_usernames_from_html(self, html):
        """Extract usernames using regex patterns"""
        patterns = [
            # Pattern for URLs like /onlyfans-models/username
            r'/onlyfans-models/([a-zA-Z0-9_-]+)',
            # Pattern for URLs with usernames in various formats
            r'/(?:model|profile|user)/([a-zA-Z0-9_-]+)',
            # Pattern for href attributes with usernames
            r'href=["\'](?:/onlyfans-models/|/model/)([a-zA-Z0-9_-]+)["\']',
            # Pattern for links ending with username
            r'/([a-zA-Z0-9_-]+)["\']\s*>',
            # Pattern for model names in text (capitalized words)
            r'#\d+\s*\n\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]

        found_usernames = set()

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                # Clean up the username
                username = match.strip()
                if len(username) > 2 and not any(x in username.lower() for x in ['page', 'category', 'tag', 'search', '?']):
                    found_usernames.add(username)

        return found_usernames

    def scrape_page(self, url):
        """Scrape a single page and extract usernames"""
        try:
            # Add random delay
            time.sleep(random.uniform(0.5, 2))

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Extract usernames
            usernames = self.extract_usernames_from_html(response.text)

            # Also look for links to other pages
            page_urls = self.extract_page_urls(response.text, url)

            return usernames, page_urls, response.text

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return set(), [], ""

    def extract_page_urls(self, html, base_url):
        """Extract URLs for other pages/pagination"""
        urls = set()

        # Look for pagination links
        pagination_patterns = [
            r'href=["\']([^"\']*page[^"\']*)["\']',
            r'href=["\']([^"\']*/page/\d+/[^"\']*)["\']',
            r'href=["\']([^"\']*\?page=\d+[^"\']*)["\']',
        ]

        for pattern in pagination_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                # Clean and build full URL
                if match.startswith('http'):
                    urls.add(match)
                else:
                    urls.add(urljoin(base_url, match))

        return urls

    def generate_username_guesses(self, base_name):
        """Generate possible username variations"""
        variations = set()

        # Basic transformations
        name_lower = base_name.lower()

        # Remove spaces
        variations.add(name_lower.replace(' ', ''))
        variations.add(name_lower.replace(' ', '_'))
        variations.add(name_lower.replace(' ', '-'))
        variations.add(name_lower.replace(' ', '.'))

        # Use first letters
        words = base_name.split()
        if len(words) > 1:
            variations.add(f"{words[0][0]}{words[1]}".lower())
            variations.add(f"{words[0]}{words[1][0]}".lower())
            variations.add(f"{words[0][0]}{words[1][0]}".lower())

        return variations

    def brute_force_usernames(self, base_url, names_list):
        """Try to access usernames based on common patterns"""
        accessible_urls = []

        print(f"\n🔍 Testing {len(names_list)} username variations...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}

            for name in names_list:
                # Generate possible usernames from the name
                possible_usernames = self.generate_username_guesses(name)

                for username in possible_usernames:
                    test_url = f"{base_url.rstrip('/')}/{username}"
                    future = executor.submit(self.test_url_exists, test_url)
                    futures[future] = test_url

            # Process results
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                try:
                    exists = future.result()
                    if exists:
                        accessible_urls.append(url)
                        print(f"✅ Found: {url}")
                except:
                    pass

        return accessible_urls

    def test_url_exists(self, url):
        """Test if a URL exists (returns 200)"""
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False

    def scrape_site_map(self, start_url):
        """Scrape the site recursively following links"""
        to_scrape = {start_url}
        scraped = set()
        all_usernames = set()

        max_pages = 50  # Limit to avoid infinite loops

        while to_scrape and len(scraped) < max_pages:
            current_url = to_scrape.pop()

            if current_url in scraped:
                continue

            print(f"📄 Scraping: {current_url}")
            scraped.add(current_url)

            usernames, new_urls, html = self.scrape_page(current_url)
            all_usernames.update(usernames)

            # Add new URLs to scrape
            for new_url in new_urls:
                if new_url not in scraped and new_url not in to_scrape:
                    if 'pimpbunny.com' in new_url:
                        to_scrape.add(new_url)

        return all_usernames

    def save_results(self, usernames, output_dir='usernames'):
        """Save extracted usernames to files"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Convert to list and sort
        username_list = sorted(list(usernames))

        # Save as text file (one per line)
        txt_file = os.path.join(output_dir, f'pimpbunny_usernames_{timestamp}.txt')
        with open(txt_file, 'w', encoding='utf-8') as f:
            for username in username_list:
                f.write(f"{username}\n")

        # Save as JSON
        json_file = os.path.join(output_dir, f'pimpbunny_usernames_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total': len(username_list),
                'scraped_at': datetime.now().isoformat(),
                'usernames': username_list
            }, f, indent=2)

        # Save as CSV
        csv_file = os.path.join(output_dir, f'pimpbunny_usernames_{timestamp}.csv')
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'url'])
            for username in username_list:
                writer.writerow([username, f"https://pimpbunny.com/onlyfans-models/{username}"])

        print(f"\n💾 Results saved:")
        print(f"  - {txt_file}")
        print(f"  - {json_file}")
        print(f"  - {csv_file}")

        return username_list

def quick_scrape():
    """Quick one-liner to scrape usernames"""
    import requests
    import re

    url = "https://pimpbunny.com/onlyfans-models/"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

    # Extract usernames from HTML
    usernames = re.findall(r'/onlyfans-models/([a-zA-Z0-9_-]+)', response.text)

    # Also look for model names in text
    model_names = re.findall(r'#\d+\s*\n?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', response.text)

    all_names = set(usernames + model_names)

    # Save to file
    with open('usernames.txt', 'w') as f:
        for name in sorted(all_names):
            f.write(f"{name}\n")

    print(f"Found {len(all_names)} unique usernames/names")
    return all_names

def main():
    """Main function with options"""
    print("="*60)
    print("PIMPBUNNY USERNAME EXTRACTOR")
    print("="*60)

    print("\nSelect scraping method:")
    print("1. Quick scrape (single page, fast)")
    print("2. Deep scrape (follow links, thorough)")
    print("3. Brute force (generate username guesses)")
    print("4. All methods combined")

    choice = input("\nEnter choice (1-4): ").strip()

    scraper = PimpBunnyUsernameScraper()
    base_url = "https://pimpbunny.com/onlyfans-models/"

    all_usernames = set()

    if choice in ['1', '4']:
        print("\n🚀 Running quick scrape...")
        usernames, _, _ = scraper.scrape_page(base_url)
        all_usernames.update(usernames)
        print(f"✅ Quick scrape found: {len(usernames)} usernames")

    if choice in ['2', '4']:
        print("\n🔍 Running deep scrape (following links)...")
        site_usernames = scraper.scrape_site_map(base_url)
        all_usernames.update(site_usernames)
        print(f"✅ Deep scrape found: {len(site_usernames)} usernames")

    if choice in ['3', '4']:
        print("\n🎯 Running brute force username generation...")
        # Use names from initial scrape or known list
        sample_names = [
            "Ella Alexandra", "Dainty Wilder", "Lily Phillips", "Ari Kytsya",
            "Jules Ari", "Caryn Beaumont", "Lena The Plug", "Hannah Owo"
        ]

        # Add names we've already found
        for username in list(all_usernames)[:20]:  # Use first 20 as samples
            if ' ' in username:
                sample_names.append(username)

        accessible = scraper.brute_force_usernames(base_url, sample_names)
        for url in accessible:
            # Extract username from URL
            username = url.rstrip('/').split('/')[-1]
            all_usernames.add(username)

        print(f"✅ Brute force found: {len(accessible)} accessible URLs")

    # Save results
    if all_usernames:
        print(f"\n📊 Total unique usernames found: {len(all_usernames)}")

        # Show samples
        print("\nSample usernames:")
        for username in sorted(list(all_usernames))[:15]:
            print(f"  • {username}")

        save = input("\n💾 Save results? (y/n): ").strip().lower()
        if save == 'y':
            saved_list = scraper.save_results(all_usernames)
            print(f"\n✅ Saved {len(saved_list)} usernames")
    else:
        print("\n❌ No usernames found!")

if __name__ == "__main__":
    main()