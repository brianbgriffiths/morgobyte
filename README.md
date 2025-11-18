# Morgobyte 🎵

A **Progressive Web App (PWA)** for managing your Yoto players and content locally. Built with Django, this application provides a fast, offline-capable interface to interact with Yoto's API.

## Quick Start

1. **Start the server:**
   ```powershell
   cd "B:\Google Drive\yoto-local-app"
   & "B:/Google Drive/yoto-local-app/.venv/Scripts/python.exe" manage.py runserver
   ```

2. **Open your browser:**
   Navigate to http://127.0.0.1:8000/

3. **Follow the setup wizard:**
   The app will guide you through:
   - Creating a Yoto OAuth application at https://dashboard.yoto.dev
   - Connecting your Yoto account
   - Authorizing the app

## ✨ UI & Design Features

### Font Awesome Integration
- **Font Awesome Pro 7.1.0** solid icons throughout the app
- All emoji icons replaced with professional vector icons
- Custom icon font (`fa-solid-900.woff2`) cached for offline use
- Base styles in `fontawesome.min.css` and `solid.css`

### Track Icons
- **Unique 16×16 pixel icons** for each chapter/track from Yoto API
- Scaled to 48×48 with **pixelated rendering** for a retro aesthetic
- Icons cached to IndexedDB alongside card covers
- Available offline once loaded
- Displayed in chapter lists and now-playing bar

### Now-Playing Player
- **Horizontal layout** with image on left, controls on right
- **Dark theme**: charcoal background (#2a2a2a) with yellow accents (#FCC921)
- Shows track icon next to chapter title
- Yellow gradient buttons with smooth hover effects
- Compact 500px width with strong visual presence

### Advanced Options Modal
- Access via settings icon in top navigation
- **Storage Info**: View IndexedDB usage for cards and images
- **Danger Zone**: Clear all data or reset specific storage
- Real-time storage size updates

### Online/Offline Indicator
- Colored circle icon in top navigation
- **Green** (#4caf50) when online, **Red** (#f44336) when offline
- Updates automatically based on network status
   - All credentials are stored locally in IndexedDB (browser storage)

That's it! No manual configuration needed.

## Features

✅ **Guided Setup Wizard** - Step-by-step OAuth setup  
✅ **Local Storage** - All data stored in browser's IndexedDB  
✅ **No Database Required** - No Django migrations needed  
✅ **Automatic Token Refresh** - Handles token expiration automatically  
✅ **User-Friendly** - Anyone can set it up and use it  
✅ **Font Awesome Icons** - Professional vector icons throughout  
✅ **Track Icons** - Unique pixelated icons for each chapter  
✅ **Dark-Themed Player** - Modern now-playing bar with yellow accents  
✅ **Offline-Ready** - Service worker v6 caches all assets and icons

## How It Works

1. **Setup Wizard** (`/api/`) - Guides users through OAuth setup
2. **OAuth Flow** - Secure authentication with Yoto
3. **Token Management** - Stores access/refresh tokens in IndexedDB
4. **Main App** (`/static/app.html`) - Browse players and library
5. **API Proxy** - Django backend proxies requests to Yoto API

## API Endpoints

All endpoints are prefixed with `/api/`

### Setup & Auth
- **GET** `/api/` - Setup wizard page
- **GET** `/api/callback` - OAuth callback handler
- **POST** `/api/auth/token` - Exchange auth code for tokens

### Yoto API
- **GET** `/api/test/` - Test API connection
- **GET** `/api/family/` - Get family information
- **GET** `/api/players/` - Get all players
- **GET** `/api/players/{player_id}/` - Get specific player
- **GET** `/api/library/` - Get content library
- **GET** `/api/cards/{card_id}/` - Get card information
- **GET** `/api/cards/{card_id}/chapters/` - Get card chapters

## Storage Architecture

### IndexedDB Stores:
- **settings** - API credentials and tokens
- **players** - Cached player data
- **library** - Cached library items
- **cards** - Individual card details and chapters
- **images** - Card covers and track icons (Base64-encoded)

### Service Worker Cache (v6):
- `app.html` - Main PWA application
- `setup.html` - Setup wizard page
- `fontawesome.min.css` + `solid.css` - Font Awesome styles
- `fa-solid-900.woff2` - Icon font file
- `pixelfont.ttf` + `Comfortaa-Regular.ttf` - Custom fonts
- Logo images and favicon
- `manifest.json` - PWA manifest

All sensitive data stays in the user's browser. Nothing is stored on the server.

## Project Structure

```
yoto-local-app/
├── api/                        # Django app
│   ├── yoto_client.py          # Yoto API client
│   ├── views.py                # API endpoints
│   └── urls.py                 # URL routes
├── static/                     # Frontend files
│   ├── setup.html              # Setup wizard
│   ├── setup-account.html      # OAuth connection page
│   ├── app.html                # Main PWA application
│   ├── sw.js                   # Service worker (v6)
│   ├── manifest.json           # PWA manifest
│   ├── css/
│   │   ├── fontawesome.min.css # Font Awesome base styles
│   │   └── solid.css           # FA solid icon definitions
│   ├── webfonts/
│   │   └── fa-solid-900.woff2  # Font Awesome icon font
│   ├── fonts/
│   │   ├── pixelfont.ttf       # Pixel font for retro text
│   │   └── Comfortaa-Regular.ttf # Title font
│   └── images/
│       ├── logo variants       # Morgobyte branding
│       └── favicon_64.png      # App icon
├── templates/                  # Django templates
│   ├── setup.html              # Setup page wrapper
│   └── oauth_callback.html     # OAuth callback handler
├── yoto_local/                 # Django project
│   ├── settings.py             # Settings
│   └── urls.py                 # Main URLs
└── manage.py                   # Django CLI
```

## Development

### Prerequisites
- Python 3.14
- Virtual environment (already set up in `.venv`)
- Modern web browser with IndexedDB support

### Running
```powershell
& "B:/Google Drive/yoto-local-app/.venv/Scripts/python.exe" manage.py runserver
```

### Adding New API Endpoints
1. Add method to `api/yoto_client.py`
2. Create view in `api/views.py`
3. Add route to `api/urls.py`

## Security Notes

- Tokens stored in IndexedDB (browser-only)
- OAuth flow uses state parameter for CSRF protection
- No credentials stored on server
- All API calls go through Django backend (no CORS issues)

## Troubleshooting

**Setup wizard not loading?**
- Check that the server is running on port 8000
- Clear browser cache and reload

**OAuth callback fails?**
- Verify redirect URI in Yoto Developer Portal matches: `http://localhost:8000/api/callback`
- Check browser console for errors

**Track icons not showing?**
- Icons load on first data fetch from Yoto API
- Check IndexedDB `images` store for cached icons
- Clear cache and refresh data if icons are missing

**Service worker not updating?**
- Hard refresh browser (Ctrl+Shift+R)
- Check Application → Service Workers in DevTools
- Current version is v6

**Storage issues?**
- Open Advanced Options modal (settings icon)
- Check storage sizes in Storage Info section
- Use Danger Zone to clear data if needed

**API calls failing?**
- Click "Refresh Data" to get new access token
- Check browser console for specific error messages
- Verify Yoto API credentials are correct

**Font Awesome icons not showing?**
- Check that service worker cached `fontawesome.min.css`, `solid.css`, and `fa-solid-900.woff2`
- Hard refresh to update service worker
- Verify files exist in `static/css/` and `static/webfonts/`

## Next Steps

Once set up, users can:
- Browse their Yoto players and content library
- View unique track icons for each chapter
- Control playback with the dark-themed now-playing bar
- Access all content offline (stored in IndexedDB)
- Monitor storage usage in Advanced Options
- Manage player settings (coming soon)
- Download content for offline playback (coming soon)
