# Quick Start Guide

## Deploy to GitHub

### Step 1: Initialize Repository

```bash
git init
git add .
git commit m "Initial commit: HostHawk Network Scanner"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `hosthawk`
3. Description: `Enterprise network scanner for security professionals`
4. Choose Public or Private
5. Click "Create repository"

### Step 3: Push to GitHub

Replace `yourusername` with your GitHub username:

```bash
git remote add origin https://github.com/yourusername/hosthawk.git
git branch M main
git push u origin main
```

### Step 4: Create a Release

When you create a release on GitHub, it will automatically post to your Discord webhook!

```bash
git tag a v1.0.0 m "Version 1.0.0"
git push origin v1.0.0
```

Then on GitHub:
1. Go to "Releases"
2. Click "Draft a new release"
3. Choose tag v1.0.0
4. Add title and release notes
5. Click "Publish release"

The Discord webhook will automatically receive:
* Tag name
* Release title
* Release notes
* Author information
* Direct link to the release

## Discord Notifications

Your repository is configured to send notifications to Discord for:

* **Pushes to main branch**: Shows commit message, author, and commit link
* **New releases**: Shows version, title, release notes, and download link

Webhook URL is already configured in `.github/workflows/discordnotify.yml`

## Usage

### Basic Scanning

```bash
hosthawk network 192.168.1.0/24
hosthawk host 192.168.1.1 p 22,80,443
```

### Web Interface

```bash
make run
```

Access at http://localhost:5000

### Docker

```bash
dockercompose up d
```

## Support

* Email: team@hosthawk.io
* Security: security@hosthawk.io
* GitHub Issues: https://github.com/yourusername/hosthawk/issues



**Ready to deploy!** 🚀
