# 🚀 Annotation Swiss Knife - Quick Start Card

## 📥 **SETUP (One-Time Only)**

### macOS/Linux:
```bash
cd ~/Downloads
unzip annotator_swiss_knife.zip
cd annotator_swiss_knife
chmod +x scripts/setup/setup.sh scripts/run/run.sh
./scripts/setup/setup.sh
```

### Windows PowerShell:
```powershell
cd $env:USERPROFILE\Downloads
# Extract zip file via right-click → "Extract All"
cd annotator_swiss_knife
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\setup\setup.ps1
```

### Windows Command Prompt:
```cmd
cd C:\Users\YourName\Downloads
# Extract zip file via right-click → "Extract All"
cd annotator_swiss_knife
scripts\setup\setup.bat
```

---

## ▶️ **RUN THE TOOL**

### macOS/Linux:
```bash
cd annotator_swiss_knife
./scripts/run/run.sh gui
```

### Windows PowerShell:
```powershell
cd annotator_swiss_knife
.\scripts\run\run.ps1 gui
```

### Windows Command Prompt:
```cmd
cd annotator_swiss_knife
scripts\run\run.bat gui
```

---

## 🔧 **QUICK FIXES**

### Permission Issues (macOS/Linux):
```bash
chmod +x scripts/setup/setup.sh scripts/run/run.sh
```

### PowerShell Policy (Windows):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Issues:
- Try `python3` instead of `python`
- Check: `python --version` or `python3 --version`

---

## 📁 **RECOMMENDED LOCATIONS**

### macOS/Linux:
- `~/Documents/tools/annotator_swiss_knife/`
- `~/Desktop/annotator_swiss_knife/`

### Windows:
- `C:\Users\YourName\Documents\tools\annotator_swiss_knife\`
- `C:\Users\YourName\Desktop\annotator_swiss_knife\`

---

## 🎯 **WHAT IT DOES**

- **Dictionary → Bullet List**: Convert dicts to formatted lists
- **Text Cleaner**: Clean markdown/JSON/code artifacts
- **JSON Visualizer**: Format and visualize JSON data
- **Conversation Visualizer**: Format chat/conversation data

---

## 📞 **NEED HELP?**

1. Check `USER_SETUP_GUIDE.md` for detailed instructions
2. Contact: [Your Name] <[Your Email]>
3. Verify Python: `python --version`

---

*💡 Tip: Bookmark this card for quick reference!*