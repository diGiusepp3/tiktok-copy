import praw
import requests
import os
import re
import time
import json
from urllib.parse import urlparse, unquote
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

class RedditMediaDownloader:
    def __init__(self, client_id, client_secret, user_agent, username=None, password=None):
        """
        Initialize Reddit API client

        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: Unique user agent string
            username: Reddit username (optional for public data)
            password: Reddit password (optional)
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password
        )

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('reddit_downloader.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Media extensions to look for
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        self.video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.gifv']

    def extract_media_urls(self, submission):
        """Extract media URLs from a Reddit submission"""
        media_urls = []

        try:
            # Direct image links
            if hasattr(submission, 'url') and submission.url:
                url = submission.url.lower()

                # Check for direct image/video links
                if any(ext in url for ext in self.image_extensions + self.video_extensions):
                    media_urls.append({
                        'url': submission.url,
                        'type': 'direct',
                        'title': submission.title,
                        'id': submission.id
                    })

                # Handle Reddit galleries
                elif 'reddit.com/gallery/' in url or hasattr(submission, 'media_metadata'):
                    media_urls.extend(self._extract_gallery_media(submission))

                # Handle i.redd.it links
                elif 'i.redd.it' in url:
                    media_urls.append({
                        'url': submission.url,
                        'type': 'reddit_image',
                        'title': submission.title,
                        'id': submission.id
                    })

                # Handle v.redd.it videos
                elif 'v.redd.it' in url:
                    video_url = self._extract_vreddit_url(submission)
                    if video_url:
                        media_urls.append({
                            'url': video_url,
                            'type': 'reddit_video',
                            'title': submission.title,
                            'id': submission.id
                        })

            # Check for embedded media in selftext
            if hasattr(submission, 'selftext') and submission.selftext:
                media_urls.extend(self._extract_urls_from_text(submission.selftext, submission))

            # Check for preview images
            if hasattr(submission, 'preview') and submission.preview:
                media_urls.extend(self._extract_preview_media(submission))

        except Exception as e:
            self.logger.error(f"Error extracting media from submission {submission.id}: {e}")

        return media_urls

    def _extract_gallery_media(self, submission):
        """Extract media from Reddit galleries"""
        gallery_media = []

        try:
            if hasattr(submission, 'media_metadata'):
                for media_id, media_item in submission.media_metadata.items():
                    if 's' in media_item and 'u' in media_item['s']:
                        url = media_item['s']['u'].replace('&amp;', '&')
                        gallery_media.append({
                            'url': url,
                            'type': 'gallery_image',
                            'title': f"{submission.title}_gallery_{media_id}",
                            'id': submission.id
                        })
        except Exception as e:
            self.logger.error(f"Error extracting gallery media: {e}")

        return gallery_media

    def _extract_vreddit_url(self, submission):
        """Extract video URL from v.redd.it posts"""
        try:
            if hasattr(submission, 'media'):
                if submission.media and 'reddit_video' in submission.media:
                    return submission.media['reddit_video']['fallback_url']

            # Alternative method
            if hasattr(submission, 'url'):
                video_id = submission.url.split('/')[-1]
                return f"https://v.redd.it/{video_id}/DASH_720.mp4"

        except Exception as e:
            self.logger.error(f"Error extracting v.redd.it URL: {e}")

        return None

    def _extract_urls_from_text(self, text, submission):
        """Extract URLs from text content"""
        urls = []
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'

        for url in re.findall(url_pattern, text):
            url_lower = url.lower()
            if any(ext in url_lower for ext in self.image_extensions + self.video_extensions):
                urls.append({
                    'url': url,
                    'type': 'text_embedded',
                    'title': submission.title,
                    'id': submission.id
                })

        return urls

    def _extract_preview_media(self, submission):
        """Extract media from preview data"""
        preview_media = []

        try:
            images = submission.preview.get('images', [])
            for img in images:
                if 'source' in img and 'url' in img['source']:
                    url = img['source']['url'].replace('&amp;', '&')
                    preview_media.append({
                        'url': url,
                        'type': 'preview_image',
                        'title': submission.title,
                        'id': submission.id
                    })
        except Exception as e:
            self.logger.error(f"Error extracting preview media: {e}")

        return preview_media

    def download_media(self, media_info, download_dir='downloads', max_retries=3):
        """Download a single media file"""
        try:
            # Create filename from title and URL
            title = media_info['title']
            url = media_info['url']

            # Clean filename
            clean_title = re.sub(r'[^\w\s-]', '', title)[:100]
            clean_title = clean_title.strip().replace(' ', '_')

            # Get file extension from URL
            parsed_url = urlparse(url)
            filename = unquote(parsed_url.path.split('/')[-1])

            # If no extension in filename, try to determine from content type
            if '.' not in filename:
                ext = '.jpg'  # default
                for img_ext in self.image_extensions:
                    if img_ext in url.lower():
                        ext = img_ext
                        break
                for vid_ext in self.video_extensions:
                    if vid_ext in url.lower():
                        ext = vid_ext
                        break
                filename = f"{clean_title}_{media_info['id']}{ext}"
            else:
                # Keep original filename but prepend with title
                filename = f"{clean_title}_{filename}"

            # Full path
            filepath = os.path.join(download_dir, filename)

            # Skip if already exists
            if os.path.exists(filepath):
                self.logger.info(f"File already exists: {filename}")
                return {'success': True, 'path': filepath, 'skipped': True}

            # Download with retries
            for attempt in range(max_retries):
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }

                    response = requests.get(url, headers=headers, stream=True, timeout=30)
                    response.raise_for_status()

                    # Save file
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    self.logger.info(f"Downloaded: {filename}")
                    return {'success': True, 'path': filepath, 'size': os.path.getsize(filepath)}

                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2 ** attempt)  # Exponential backoff

        except Exception as e:
            self.logger.error(f"Failed to download {media_info.get('url', 'unknown')}: {e}")
            return {'success': False, 'error': str(e), 'url': media_info.get('url')}

    def get_user_submissions(self, username, limit=None, sort='new', time_filter='all'):
        """Get all submissions from a user"""
        try:
            user = self.reddit.redditor(username)

            submissions = []
            if limit:
                submissions = list(user.submissions.new(limit=limit))
            else:
                # Try to get as many as possible
                submissions = list(user.submissions.new(limit=1000))

            self.logger.info(f"Found {len(submissions)} submissions from u/{username}")
            return submissions

        except Exception as e:
            self.logger.error(f"Error fetching submissions for u/{username}: {e}")
            return []

    def download_all_user_media(self, username, download_dir=None, max_workers=5, limit=None):
        """Main function to download all media from a user"""
        if download_dir is None:
            download_dir = f"downloads/{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        os.makedirs(download_dir, exist_ok=True)

        self.logger.info(f"Starting download for u/{username}")
        self.logger.info(f"Download directory: {download_dir}")

        # Get user submissions
        submissions = self.get_user_submissions(username, limit=limit)

        if not submissions:
            self.logger.warning(f"No submissions found for u/{username}")
            return []

        # Extract all media URLs
        all_media = []
        for submission in submissions:
            media_urls = self.extract_media_urls(submission)
            all_media.extend(media_urls)

        self.logger.info(f"Found {len(all_media)} media items to download")

        # Save metadata
        metadata = {
            'username': username,
            'download_date': datetime.now().isoformat(),
            'total_submissions': len(submissions),
            'total_media': len(all_media),
            'media_items': all_media
        }

        with open(os.path.join(download_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # Download all media concurrently
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_media = {
                executor.submit(self.download_media, media, download_dir): media
                for media in all_media
            }

            for future in as_completed(future_to_media):
                media = future_to_media[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Exception in download: {e}")
                    results.append({'success': False, 'error': str(e), 'url': media.get('url')})

        # Summary
        successful = sum(1 for r in results if r.get('success'))
        skipped = sum(1 for r in results if r.get('skipped', False))
        failed = len(results) - successful

        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"DOWNLOAD SUMMARY for u/{username}")
        self.logger.info(f"{'='*50}")
        self.logger.info(f"Total media found: {len(all_media)}")
        self.logger.info(f"Successfully downloaded: {successful}")
        self.logger.info(f"Already existed (skipped): {skipped}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Download directory: {download_dir}")

        return results

def main():
    """Main function with configuration"""
    print("Reddit Media Downloader")
    print("="*50)

    # Configuration - YOU NEED TO FILL THESE IN
    config = {
        'client_id': 'YOUR_CLIENT_ID',      # From Reddit app
        'client_secret': 'YOUR_CLIENT_SECRET',  # From Reddit app
        'user_agent': 'MediaDownloader/1.0 by YourUsername',
        'username': None,  # Optional - only needed for private content
        'password': None   # Optional
    }

    # Target username
    target_user = 'oheytherehellohi'

    # Ask for configuration if not set
    if config['client_id'] == 'YOUR_CLIENT_ID':
        print("\n⚠️  You need to set up Reddit API credentials first!")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Click 'create app' or 'create another app'")
        print("3. Fill in the form (select 'script' type)")
        print("4. Copy client_id (under the app name) and client_secret")
        print("\nEnter your credentials:")

        config['client_id'] = input("Client ID: ").strip()
        config['client_secret'] = input("Client Secret: ").strip()
        config['user_agent'] = input("User Agent (default: MediaDownloader/1.0): ").strip() or 'MediaDownloader/1.0'

        use_auth = input("Use authentication? (y/n, needed for NSFW/private): ").lower().strip()
        if use_auth.startswith('y'):
            config['username'] = input("Reddit Username: ").strip()
            config['password'] = input("Reddit Password: ").strip()

    # Create downloader instance
    downloader = RedditMediaDownloader(**config)

    # Configuration options
    print(f"\nDownloading media from u/{target_user}")
    print("\nOptions:")
    print("1. Quick download (latest 100 posts)")
    print("2. Comprehensive download (as many as possible)")
    print("3. Custom limit")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == '1':
        limit = 100
    elif choice == '2':
        limit = None  # Get as many as possible
    elif choice == '3':
        try:
            limit = int(input("Enter number of posts to check: ").strip())
        except:
            limit = 100
            print(f"Invalid input, using default: {limit}")
    else:
        limit = 100

    # Ask for concurrent downloads
    try:
        workers = int(input(f"Concurrent downloads (default 3): ").strip() or "3")
    except:
        workers = 3

    # Start download
    print(f"\nStarting download with configuration:")
    print(f"- User: u/{target_user}")
    print(f"- Post limit: {'All available' if limit is None else limit}")
    print(f"- Concurrent downloads: {workers}")

    confirm = input("\nProceed? (y/n): ").lower().strip()

    if confirm.startswith('y'):
        try:
            results = downloader.download_all_user_media(
                username=target_user,
                max_workers=workers,
                limit=limit
            )

            # Show failures if any
            failures = [r for r in results if not r.get('success') and not r.get('skipped', False)]
            if failures:
                print(f"\n⚠️  {len(failures)} downloads failed:")
                for fail in failures[:5]:  # Show first 5 failures
                    print(f"  - {fail.get('url', 'Unknown URL')}: {fail.get('error', 'Unknown error')}")

                if len(failures) > 5:
                    print(f"  ... and {len(failures) - 5} more")

            print(f"\n✅ Check 'downloads' folder for your files!")
            print(f"📊 Summary saved in metadata.json")

        except Exception as e:
            print(f"❌ Error during download: {e}")
            print("Check reddit_downloader.log for details")
    else:
        print("Download cancelled.")

if __name__ == "__main__":
    main()