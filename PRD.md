{
  "original_problem_statement": "Transform into an adult TikTok clone with integrated ChatGPT admin panel. Main app is a video/image sharing platform for adults (like OnlyFans + TikTok). ChatGPT is secondary feature for admin use.",
  "user_choices": "MySQL database (mgielen.zapto.org), File storage at /mnt/bigdisk/images/, Scrapers must work, Admin can bulk create posts, Users can upload content, Subscription system",
  "key_functionalities": [
    "Adult Content Feed (TikTok-style vertical scrolling)",
    "User Authentication (Register/Login)",
    "Content Upload (Images & Videos)",
    "Likes, Comments, Shares",
    "Follow/Unfollow Users",
    "Subscription System (OnlyFans-style)",
    "Admin Panel with ChatGPT",
    "Scraper Integration for bulk content",
    "File Storage Management"
  ],
  "app_type": "adult_content_platform",
  "functionalities_and_pages": [
    "Auth Screen - Login/Register with dark theme",
    "Home Feed - Vertical scrolling video/image feed",
    "Discover - Explore content and creators",
    "Upload - Content upload for creators",
    "Profile - User profile with stats",
    "Admin Panel - ChatGPT + Scraper controls (admin only)"
  ],
  "target_audience": "18+ users, content creators, subscribers",
  "constraints_and_context": "Dark sultry theme for adults. MySQL database at mgielen.zapto.org. File storage: /mnt/bigdisk/images/{username}/{type}/. Tech stack: React frontend + FastAPI backend + MySQL. JWT authentication. Scrapers: OF-Scraper, fansly-scraper, nudogram, PimpBunny, PassesDL, OSINT, mediaCollector, redditMedia.",
  "database_schema": {
    "users": "id, username, email, password_hash, display_name, bio, avatar_url, is_admin, is_creator, is_verified, followers_count, following_count, likes_count",
    "posts": "id, user_id, type (image/video), file_path, thumbnail_path, caption, likes_count, comments_count, shares_count, views_count, is_public, subscribers_only",
    "subscriptions": "id, subscriber_user_id, creator_user_id, price, status, expires_at",
    "likes": "id, user_id, post_id",
    "comments": "id, user_id, post_id, content, likes_count",
    "follows": "id, follower_id, following_id",
    "admin_scrapers_log": "id, scraper_name, status, items_scraped, error_message, started_at, completed_at"
  },
  "test_credentials": {
    "admin": "admin / admin123",
    "creator": "creator1 / creator123",
    "user": "user1 / user123"
  }
}