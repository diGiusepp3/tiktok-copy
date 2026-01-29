# Clone App - OnlyFans + TikTok Hybrid Platform

## Original Problem Statement
Build a media management platform combining OnlyFans and TikTok features with:
- TikTok-style vertical video feed
- OnlyFans-style creator profiles
- Media scraping (yt-dlp + OFScraper)
- File manager for 950K+ files
- Server CLI terminal
- MySQL database with real auth

## Architecture
- **Backend**: FastAPI (Python) with MySQL connector
- **Frontend**: React 19 with Tailwind CSS, Framer Motion
- **Database**: MySQL at mgielen.zapto.org:3306
- **Storage**: /mnt/sata_m2 (1TB SSD)
- **Auth**: JWT-based with bcrypt password hashing

## User Personas
1. **Content Creators**: Upload/manage media, build subscriber base
2. **Content Consumers**: Browse feed, discover creators, subscribe
3. **Power Users/Admins**: Manage files, use CLI, run scrapers

## Core Features Implemented
### Phase 1 (Complete - Jan 2025)
- [x] TikTok-style vertical video feed with snap scroll
- [x] Creator discovery with search and filters
- [x] User authentication (register/login)
- [x] Creator profile pages with media grid
- [x] URL scraper with yt-dlp analysis
- [x] OFScraper CLI integration
- [x] File manager with breadcrumb navigation
- [x] Server terminal with command execution
- [x] Chat assistant placeholder UI
- [x] Responsive dark theme (Midnight Velvet)
- [x] MySQL database with auto-initialization

## API Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication
- `GET /api/auth/me` - Current user info
- `GET /api/feed` - Video feed content
- `GET /api/creators` - Discover creators
- `GET /api/creators/{username}` - Creator profile
- `POST /api/scraper/analyze` - Analyze URL for media
- `POST /api/scraper/download` - Start download task
- `POST /api/cli/execute` - Execute CLI command
- `GET /api/files/browse` - Browse file system
- `GET /api/system/stats` - Disk usage stats

## Prioritized Backlog
### P0 (Critical)
- [ ] Video upload functionality
- [ ] Real media storage integration
- [ ] Subscription payments

### P1 (High)
- [ ] Comments system
- [ ] Direct messaging
- [ ] AI-powered chat assistant (connect to LLM)
- [ ] Media import from legacy folder

### P2 (Medium)
- [ ] Notifications
- [ ] Creator analytics dashboard
- [ ] Content moderation
- [ ] Search improvements

## Environment Variables
```
MYSQL_HOST=mgielen.zapto.org
MYSQL_PORT=3306
MYSQL_USER=matthias
MYSQL_PASSWORD=DigiuSeppe2018___
MYSQL_DATABASE=clone_app
JWT_SECRET=<secret>
MEDIA_BASE_PATH=/mnt/sata_m2
LEGACY_MEDIA_PATH=/mnt/bigdisk/images
```

## Next Steps
1. Import existing media from /mnt/bigdisk/images
2. Connect chat assistant to AI API
3. Add video upload with transcoding
4. Implement subscription system
