# 🚀 Quick Start Guide - Morgobyte

## First Time Setup (5 minutes)

### Step 1: Start the Server
1. Open PowerShell or Terminal
2. Navigate to the project folder:
   ```powershell
   cd "B:\Google Drive\yoto-local-app"
   ```
3. Run the server:
   ```powershell
   & "B:/Google Drive/yoto-local-app/.venv/Scripts/python.exe" manage.py runserver
   ```

### Step 2: Open Your Browser
Visit: **http://127.0.0.1:8000/**

You'll see the setup wizard automatically!

### Step 3: Follow the Wizard
The setup wizard will guide you through:

1. **Welcome Screen** - Click "Get Started"

2. **Create OAuth App**
   - Go to https://dashboard.yoto.dev
   - Sign in with your Yoto account
   - Create a new application:
     - **Name:** Yoto Local App
     - **Redirect URI:** http://localhost:8000/api/callback
   - Copy your Client ID and Client Secret

3. **Enter Credentials**
   - Paste your Client ID
   - Paste your Client Secret
   - Click "Connect to Yoto"

4. **Authorize**
   - A popup will open to Yoto's authorization page
   - Log in and authorize the app
   - The popup will close automatically

5. **Done!**
   - Your app is now connected
   - Click "Launch App" to start using it

## Using the App

Once set up, you can:
- ✅ View all your Yoto players
- ✅ Browse your content library with unique track icons
- ✅ Control playback with the dark-themed now-playing bar
- ✅ See real-time online/offline status (green/red indicator)
- ✅ Access advanced options for storage management
- ✅ All data cached locally for offline access (including track icons)

## Need Help?

**Server won't start?**
- Make sure you're in the right directory
- Check that Python 3.14 is installed

**Setup wizard not loading?**
- Make sure server is running on port 8000
- Try a different browser
- Clear browser cache

**OAuth fails?**
- Double-check your Client ID and Secret
- Verify the redirect URI is exactly: `http://localhost:8000/api/callback`
- Make sure you're logged into Yoto in the browser

**Can't see your data?**
- Click the "Refresh Data" button
- Check browser console for errors (F12)
- Verify your Yoto account has players and content

**Track icons not showing?**
- Icons load on first data fetch and are cached
- Clear cache and refresh if missing
- Check Advanced Options → Storage Info

**Service worker issues?**
- Hard refresh (Ctrl+Shift+R)
- Current version is v6
- Check Application tab in DevTools
## Sharing with Others

Want to share this app with friends/family?

1. Give them a copy of this folder
2. They follow this Quick Start Guide
3. Each person creates their own OAuth app
4. Each person's data is separate and private

**Note:** Everyone needs their own Yoto account and OAuth credentials!

## Tips & Tricks

- 🔄 **Refresh Data** button updates from Yoto servers
- 💾 **Everything stored locally** in your browser (including track icons)
- 🔒 **Privacy first** - no data leaves your computer
- ⚡ **Fast** - cached data loads instantly
- 🌐 **Works offline** once data is cached
- 🎨 **Font Awesome icons** throughout the app for a polished look
- 🎵 **Track icons** - each chapter has a unique 16×16 pixel icon (scaled to 48×48)
- 🌙 **Dark-themed player** - modern horizontal now-playing bar with yellow accents
- ⚙️ **Advanced Options** - manage storage via settings icon in top navigation
- 🟢🔴 **Status indicator** - green when online, red when offline

Enjoy your Morgobyte app! 🎵