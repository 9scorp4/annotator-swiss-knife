# Distribution Guide - Google Drive Method

## How to Share This Tool via Google Drive

Since your team uses Google Drive as the primary cloud framework, here's the streamlined process to distribute this annotation toolkit:

## Step-by-Step Distribution Process

### 1. Create the Distribution Package

```bash
cd /Users/username/Documents/repos
zip -r annotator_swiss_knife_v0.2.0.zip annotator_swiss_knife/
```

### 2. Upload to Google Drive

1. **Go to Google Drive** (drive.google.com)
2. **Navigate to your team's shared folder** or create a new one
3. **Upload the zip file:**
   - Click "New" → "File upload"
   - Select `annotator_swiss_knife_v0.2.0.zip`
   - Wait for upload to complete

### 3. Set Sharing Permissions

1. **Right-click** on the uploaded zip file
2. **Select "Share"**
3. **Choose appropriate permissions:**
   - **For team members:** "Anyone with the link can view"
   - **For specific people:** Add their email addresses
   - **Recommended:** "Viewer" access (prevents accidental modifications)

### 4. Copy the Share Link

1. **Click "Copy link"** from the sharing dialog
2. **Save this link** - you'll include it in your distribution message

### 5. Create Distribution Message

Use this template for sharing with your team:

```
Subject: Annotation Swiss Knife - Data Processing Tool

Hi team,

I've created a simple annotation toolkit that might be useful for our data processing tasks.

📥 Download: [Google Drive Link]
📖 Setup Guide: See USER_SETUP_GUIDE.md in the zip file
🚀 Quick Start: See QUICK_START_CARD.md for instant commands

Features:
- Dictionary to Bullet List conversion
- Text cleaning from markdown/JSON
- JSON visualization and formatting  
- Conversation data formatting

Setup is simple - just extract and run one setup script!

Instructions:
1. Download annotator_swiss_knife_v0.2.0.zip from the link above
2. Extract to your preferred location
3. Open Terminal/Command Prompt and navigate to the folder
4. Run: ./scripts/setup/setup.sh (macOS/Linux) or scripts\setup\setup.bat (Windows)
5. Run: ./scripts/run/run.sh gui (macOS/Linux) or scripts\run\run.bat gui (Windows)

Let me know if you have questions or feedback!

Best,
[Your Name]
[Your Email]
```

## What to Include in Your Distribution

### Essential Files (All Included in Zip)
- The entire `annotator_swiss_knife/` folder
- `USER_SETUP_GUIDE.md` - Detailed setup instructions
- `QUICK_START_CARD.md` - Quick reference commands
- `README.md` - Full documentation
- `requirements.txt` - Python dependencies
- All scripts in `scripts/` folder

## Google Drive Best Practices

### Folder Organization
Create a clear folder structure in your team's Google Drive:
```
Team Tools/
├── Annotation Swiss Knife/
│   ├── annotator_swiss_knife_v0.2.0.zip
│   ├── Release Notes.md (optional)
│   └── User Feedback/ (for collecting feedback)
```

### Version Management
- **Use version numbers** in zip file names (e.g., `v0.2.0`)
- **Keep previous versions** for rollback if needed
- **Update sharing links** when you release new versions
- **Notify team** of updates via email or Workplace

### Access Control
- **Team folder:** Use "Anyone with the link can view" for easy sharing
- **Sensitive versions:** Use specific email addresses for restricted access
- **Download tracking:** Google Drive shows who accessed files (useful for adoption metrics)

## Security Considerations

✅ **Safe for Meta Devices:**
- Runs from source code (no unsigned executables)
- Uses standard Python libraries
- No network access required
- No sensitive data handling

✅ **Google Drive Compliant:**
- Approved cloud storage at Meta
- Works within Contingent Worker access limitations
- Maintains audit trail of downloads
- Easy permission management

## Tips for Success

1. **Test the download process:** Try downloading and extracting from Google Drive yourself
2. **Clear file naming:** Use descriptive names with version numbers
3. **Monitor usage:** Check Google Drive analytics to see adoption
4. **Gather feedback:** Create a shared document for user suggestions
5. **Regular updates:** Keep the tool current based on team needs

## Troubleshooting Distribution Issues

### Common Google Drive Issues:
- **Large file uploads:** May take time, ensure stable internet
- **Permission errors:** Double-check sharing settings
- **Download failures:** Users may need to try different browsers
- **Extraction issues:** Remind users about the setup guides

### User Support Strategy:
- **First response:** Point to `USER_SETUP_GUIDE.md`
- **Quick fixes:** Share `QUICK_START_CARD.md` commands
- **Complex issues:** Offer to help via video call or screen share
- **Documentation:** Update guides based on common questions

## Alternative: Direct Google Drive Integration

For future versions, consider:
- **Google Colab notebooks** for web-based usage
- **Google Apps Script** for simple automation
- **Direct integration** with Google Sheets for data processing

---

*This distribution method leverages your team's existing Google Drive workflow while maintaining security and ease of use.*