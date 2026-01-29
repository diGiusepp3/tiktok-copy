import requests
import json
from datetime import datetime
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_platform(platform, url, username):
    """Check if a username exists on a specific platform"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)

        if response.status_code == 200:
            # Common "not found" indicators
            not_found_indicators = [
                'not found', '404', 'does not exist', 'no longer available',
                'page not found', 'user not found', 'profile not found',
                '找不到', '未被发现', 'sorry, this page', 'error 404',
                'this account doesn', 'doesn\'t exist', 'deactivated',
                'suspended', 'isn\'t available'
            ]

            content_lower = response.text.lower()

            # Check if any "not found" indicator is in the page
            if any(indicator in content_lower for indicator in not_found_indicators):
                return platform, url, "Not found", response.status_code, None
            else:
                # Try to extract display name or profile info
                display_name = extract_display_name(response.text, platform, username)
                return platform, url, "Found", response.status_code, display_name

        elif response.status_code == 403:
            return platform, url, "Private/Restricted", response.status_code, None
        elif response.status_code == 429:
            # Rate limited
            time.sleep(2)
            return platform, url, "Rate limited", response.status_code, None
        elif response.status_code == 404:
            return platform, url, "Not found", response.status_code, None
        else:
            return platform, url, f"HTTP {response.status_code}", response.status_code, None

    except requests.RequestException as e:
        return platform, url, f"Error: {str(e)[:50]}", None, None
    except Exception as e:
        return platform, url, f"Error: {str(e)[:50]}", None, None

def extract_display_name(html_content, platform, username):
    """Extract display name from platform HTML"""
    try:
        # Platform-specific extraction patterns
        patterns = {
            'Twitter': [r'<title>([^<]+) \(@[^)]+\)</title>', r'<meta name="description" content="([^"]+)"'],
            'Instagram': [r'<title>@{} \(([^)]+)\)'.format(username), r'"full_name":"([^"]+)"'],
            'GitHub': [r'<title>{} \(([^)]+)\)'.format(username), r'<span class="p-name vcard-fullname"[^>]*>([^<]+)</span>'],
            'Reddit': [r'<title>u/{} - Reddit</title>'.format(username)],
            'YouTube': [r'<title>([^<]+) - YouTube</title>', r'"author":"([^"]+)"'],
        }

        if platform in patterns:
            for pattern in patterns[platform]:
                import re
                match = re.search(pattern, html_content)
                if match:
                    return match.group(1).strip()
    except:
        pass
    return None

def quick_username_search(username):
    """Quick username search across major platforms"""

    print(f"Searching for username: {username}")
    print("="*50)

    platforms = {
        "linktree": f"https://linktr.ee/{username}",
        "Fansly": f"https://fansly.com/@{username}",
        "Passes" : f"https://passes.com/@{username}",
        "Twitter": f"https://twitter.com/{username}",
        "Instagram": f"https://instagram.com/{username}",
        "GitHub": f"https://github.com/{username}",
        "Reddit": f"https://reddit.com/user/{username}",
        "YouTube": f"https://youtube.com/@{username}",
        "TikTok": f"https://tiktok.com/@{username}",
        "Twitch": f"https://twitch.tv/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "Pinterest": f"https://pinterest.com/{username}",
        "Medium": f"https://medium.com/@{username}",
        "Dev.to": f"https://dev.to/{username}",
        "Keybase": f"https://keybase.io/{username}",
        "Facebook": f"https://facebook.com/{username}",
        "LinkedIn": f"https://linkedin.com/in/{username}",
        "Snapchat": f"https://snapchat.com/add/{username}",
        "Telegram": f"https://t.me/{username}",
        "Discord": "https://discord.com/users/",  # Note: Requires user ID, not username
        "Spotify": f"https://open.spotify.com/user/{username}",
        "SoundCloud": f"https://soundcloud.com/{username}",
        "Mixcloud": f"https://mixcloud.com/{username}",
        "Last.fm": f"https://last.fm/user/{username}",
        "Flickr": f"https://flickr.com/people/{username}",
        "Imgur": f"https://imgur.com/user/{username}",
        "DeviantArt": f"https://deviantart.com/{username}",
        "Behance": f"https://behance.net/{username}",
        "Dribbble": f"https://dribbble.com/{username}",
        "ArtStation": f"https://artstation.com/{username}",
        "Patreon": f"https://patreon.com/{username}",
        "OnlyFans": f"https://onlyfans.com/{username}",
        "Substack": f"https://substack.com/profile/{username}",
        "Letterboxd": f"https://letterboxd.com/{username}",
        "Goodreads": f"https://goodreads.com/{username}",
        "Strava": f"https://strava.com/athletes/{username}",
        "Untappd": f"https://untappd.com/user/{username}",
        "Duolingo": f"https://duolingo.com/profile/{username}",
        "Chess.com": f"https://chess.com/member/{username}",
        "Lichess": f"https://lichess.org/@/{username}",
        "Replit": f"https://replit.com/@{username}",
        "CodePen": f"https://codepen.io/{username}",
        "Stack Overflow": f"https://stackoverflow.com/users/{username}",
        "NPM": f"https://npmjs.com/~{username}",
        "PyPI": f"https://pypi.org/user/{username}",
        "Docker": f"https://hub.docker.com/u/{username}",
        "Roblox": f"https://roblox.com/users/{username}",
        "Epic Games": f"https://epicgames.com/account/{username}",
        "Xbox": f"https://xboxgamertag.com/search/{username}",
        "PlayStation": f"https://psnprofiles.com/{username}",
        "Tumblr": f"https://{username}.tumblr.com",
        "WordPress": f"https://{username}.wordpress.com",
        "Blogger": f"https://{username}.blogspot.com",
        "Wikipedia": f"https://en.wikipedia.org/wiki/User:{username}",
        "eBay": f"https://www.ebay.com/usr/{username}",
        "Etsy": f"https://etsy.com/people/{username}",
        "PayPal": f"https://paypal.me/{username}",
        "Venmo": f"https://venmo.com/{username}",
        "CashApp": f"https://cash.app/${username}",
        "GoFundMe": f"https://gofundme.com/f/{username}",
        "Kickstarter": f"https://kickstarter.com/profile/{username}",
    }

    results = []
    found_count = 0

    # Use threading for faster checking
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_platform = {
            executor.submit(check_platform, platform, url, username): platform
            for platform, url in platforms.items()
        }

        for future in as_completed(future_to_platform):
            platform = future_to_platform[future]
            try:
                platform_name, url, status, status_code, display_name = future.result()

                result = {
                    "platform": platform_name,
                    "url": url,
                    "status": status,
                    "status_code": status_code,
                    "display_name": display_name
                }
                results.append(result)

                # Print result
                if status == "Found":
                    emoji = "✅"
                    found_count += 1
                    extra = f" | Display: {display_name}" if display_name else ""
                elif status == "Private/Restricted":
                    emoji = "🔒"
                    extra = " (Private)"
                elif "Error" in status:
                    emoji = "❌"
                    extra = ""
                else:
                    emoji = "❌"
                    extra = ""

                print(f"{emoji} {platform_name}: {status}{extra}")

            except Exception as e:
                print(f"❌ {platform}: Error - {str(e)[:50]}")

    # Sort results by status (Found first)
    results.sort(key=lambda x: (x['status'] != 'Found', x['platform']))

    return results, found_count

def search_multiple_usernames(wordlist_path):
    """Search for multiple usernames from a wordlist"""
    try:
        with open(wordlist_path, 'r', encoding='utf-8') as f:
            usernames = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        print(f"Loaded {len(usernames)} usernames from {wordlist_path}")
        print("="*50)

        all_results = {}

        for i, username in enumerate(usernames, 1):
            print(f"\n[{i}/{len(usernames)}] Searching: {username}")

            try:
                results, found_count = quick_username_search(username)
                all_results[username] = {
                    'results': results,
                    'found_count': found_count,
                    'total_checked': len(results)
                }

                # Small delay to avoid rate limiting
                if i < len(usernames):
                    time.sleep(1)

            except Exception as e:
                print(f"❌ Error searching {username}: {e}")
                all_results[username] = {
                    'error': str(e),
                    'results': [],
                    'found_count': 0,
                    'total_checked': 0
                }

        return all_results

    except FileNotFoundError:
        print(f"❌ Error: Wordlist file not found: {wordlist_path}")
        return {}
    except Exception as e:
        print(f"❌ Error reading wordlist: {e}")
        return {}

def save_results_single(username, results, found_count):
    """Save results for a single username"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"osint_results_{username}_{timestamp}.json"

    output = {
        "username": username,
        "search_date": datetime.now().isoformat(),
        "total_found": found_count,
        "total_checked": len(results),
        "results": results
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Also save a simplified CSV version
    csv_filename = f"osint_results_{username}_{timestamp}.csv"
    with open(csv_filename, 'w', encoding='utf-8') as f:
        f.write("Platform,URL,Status,Status Code,Display Name\n")
        for result in results:
            f.write(f"{result['platform']},{result['url']},{result['status']},{result['status_code'] or ''},{result['display_name'] or ''}\n")

    return filename, csv_filename

def save_results_multiple(all_results):
    """Save results for multiple usernames"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save detailed JSON
    json_filename = f"osint_wordlist_results_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    # Save summary CSV
    csv_filename = f"osint_wordlist_summary_{timestamp}.csv"
    with open(csv_filename, 'w', encoding='utf-8') as f:
        f.write("Username,Found Count,Total Checked,Found Platforms\n")
        for username, data in all_results.items():
            if 'error' in data:
                f.write(f"{username},ERROR,0,{data['error']}\n")
            else:
                found_platforms = []
                for result in data['results']:
                    if result['status'] == 'Found':
                        found_platforms.append(result['platform'])

                platforms_str = '; '.join(found_platforms)
                f.write(f"{username},{data['found_count']},{data['total_checked']},\"{platforms_str}\"\n")

    # Save detailed CSV
    detailed_csv = f"osint_wordlist_detailed_{timestamp}.csv"
    with open(detailed_csv, 'w', encoding='utf-8') as f:
        f.write("Username,Platform,URL,Status,Status Code,Display Name\n")
        for username, data in all_results.items():
            if 'results' in data:
                for result in data['results']:
                    f.write(f"{username},{result['platform']},{result['url']},{result['status']},{result['status_code'] or ''},{result['display_name'] or ''}\n")

    return json_filename, csv_filename, detailed_csv

def main():
    """Main function with interactive menu"""
    print("="*60)
    print("🕵️‍♂️  ADVANCED USERNAME OSINT TOOL")
    print("="*60)
    print()
    print("Select mode:")
    print("1. Search for a single username")
    print("2. Search multiple usernames from wordlist")
    print("3. Exit")
    print()

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        # Single username search
        username = input("\nEnter username to search: ").strip()

        if not username:
            print("❌ Error: Username cannot be empty!")
            return

        confirm = input(f"\nSearch for username '{username}'? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Search cancelled.")
            return

        print("\n" + "="*60)
        results, found_count = quick_username_search(username)

        # Display summary
        print("\n" + "="*60)
        print("📊 SEARCH SUMMARY")
        print("="*60)
        print(f"Username: {username}")
        print(f"Found on: {found_count} platforms")
        print(f"Total checked: {len(results)} platforms")

        if found_count > 0:
            print("\n✅ Found on:")
            for result in results:
                if result['status'] == 'Found':
                    display_info = f" - {result['display_name']}" if result['display_name'] else ""
                    print(f"  • {result['platform']}: {result['url']}{display_info}")

        # Save results
        save_option = input("\nSave results? (y/n): ").strip().lower()
        if save_option in ['y', 'yes']:
            json_file, csv_file = save_results_single(username, results, found_count)
            print(f"✅ Results saved to:")
            print(f"   JSON: {json_file}")
            print(f"   CSV: {csv_file}")

    elif choice == "2":
        # Wordlist search
        print("\n📁 Wordlist format:")
        print("  - One username per line")
        print("  - Empty lines and lines starting with # are ignored")
        print("  - File should be in UTF-8 encoding")
        print()

        wordlist_path = input("Enter path to wordlist file: ").strip()

        if not os.path.exists(wordlist_path):
            print(f"❌ Error: File not found: {wordlist_path}")
            return

        try:
            with open(wordlist_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for line in f if line.strip() and not line.startswith('#'))

            if line_count == 0:
                print("❌ Error: Wordlist file is empty or contains no valid usernames")
                return

            print(f"Found {line_count} usernames in wordlist")

            confirm = input(f"\nSearch {line_count} usernames? This may take a while. (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("Search cancelled.")
                return

            print("\n" + "="*60)
            all_results = search_multiple_usernames(wordlist_path)

            # Display summary
            print("\n" + "="*60)
            print("📊 WORDLIST SEARCH SUMMARY")
            print("="*60)

            total_found = 0
            total_checked = 0

            for username, data in all_results.items():
                if 'found_count' in data:
                    total_found += data['found_count']
                    total_checked += data['total_checked']

            print(f"Total usernames searched: {len(all_results)}")
            print(f"Total platforms found: {total_found}")

            # Show top results
            print("\n🏆 Most active usernames:")
            sorted_usernames = sorted(
                [(u, d['found_count']) for u, d in all_results.items() if 'found_count' in d],
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10

            for username, count in sorted_usernames:
                if count > 0:
                    print(f"  {username}: {count} platforms")

            # Save results
            save_option = input("\nSave results? (y/n): ").strip().lower()
            if save_option in ['y', 'yes']:
                json_file, csv_file, detailed_csv = save_results_multiple(all_results)
                print(f"✅ Results saved to:")
                print(f"   Detailed JSON: {json_file}")
                print(f"   Summary CSV: {csv_file}")
                print(f"   Detailed CSV: {detailed_csv}")

        except Exception as e:
            print(f"❌ Error: {e}")

    elif choice == "3":
        print("\nGoodbye!")
        return

    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Search interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()