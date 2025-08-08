# Annotation Swiss Knife - User Setup Guide

## Quick Start Guide

This guide will help you extract, set up, and run the Annotation Swiss Knife toolkit on your system.

---

## 📋 Prerequisites

- **Python 3.8 or higher** (usually pre-installed on Meta devices)
- **Terminal/Command Prompt access**
- **No admin privileges required**

---

## 🖥️ Platform-Specific Instructions

### 🍎 **macOS/Linux Users**

#### Step 1: Extract the Files
1. **Download** the `annotator_swiss_knife.zip` file to your desired location
2. **Navigate** to where you downloaded the file:
   ```bash
   cd ~/Downloads  # or wherever you downloaded the file
   ```
3. **Extract** the zip file:
   ```bash
   unzip annotator_swiss_knife.zip
   ```
4. **Navigate** into the extracted folder:
   ```bash
   cd annotator_swiss_knife
   ```

#### Step 2: One-Time Setup
Run the setup script to create a virtual environment and install dependencies:
```bash
chmod +x scripts/setup/setup.sh
./scripts/setup/setup.sh
```

#### Step 3: Launch the Application
```bash
chmod +x scripts/run/run.sh
./scripts/run/run.sh gui
```

---

### 🪟 **Windows Users**

#### Step 1: Extract the Files
1. **Download** the `annotator_swiss_knife.zip` file to your desired location (e.g., `C:\Users\YourName\Downloads\`)
2. **Right-click** on the zip file and select "Extract All..."
3. **Choose** a destination folder (e.g., `C:\Users\YourName\Documents\`)
4. **Open** Command Prompt or PowerShell and navigate to the extracted folder:

**Using Command Prompt:**
```cmd
cd C:\Users\YourName\Documents\annotator_swiss_knife
```

**Using PowerShell:**
```powershell
cd C:\Users\YourName\Documents\annotator_swiss_knife
```

#### Step 2: One-Time Setup

**Using PowerShell (Recommended):**
```powershell
# Allow script execution (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run setup
.\scripts\setup\setup.ps1
```

**Using Command Prompt:**
```cmd
scripts\setup\setup.bat
```

#### Step 3: Launch the Application

**Using PowerShell:**
```powershell
.\scripts\run\run.ps1 gui
```

**Using Command Prompt:**
```cmd
scripts\run\run.bat gui
```

---

## 📁 Recommended Directory Structure

Choose one of these locations for best organization:

### macOS/Linux:
```
~/Documents/tools/annotator_swiss_knife/
~/Desktop/annotator_swiss_knife/
~/tools/annotator_swiss_knife/
```

### Windows:
```
C:\Users\YourName\Documents\tools\annotator_swiss_knife\
C:\Users\YourName\Desktop\annotator_swiss_knife\
C:\tools\annotator_swiss_knife\
```

---

## 🔧 Complete Step-by-Step Example

### macOS Example:
```bash
# 1. Navigate to Downloads
cd ~/Downloads

# 2. Extract the zip file
unzip annotator_swiss_knife.zip

# 3. Move to a better location (optional)
mv annotator_swiss_knife ~/Documents/tools/

# 4. Navigate to the tool directory
cd ~/Documents/tools/annotator_swiss_knife

# 5. Make scripts executable and run setup
chmod +x scripts/setup/setup.sh scripts/run/run.sh
./scripts/setup/setup.sh

# 6. Launch the application
./scripts/run/run.sh gui
```

### Windows PowerShell Example:
```powershell
# 1. Navigate to Downloads
cd $env:USERPROFILE\Downloads

# 2. Extract (assuming you've already extracted via right-click)
# Move to a better location (optional)
Move-Item annotator_swiss_knife $env:USERPROFILE\Documents\tools\

# 3. Navigate to the tool directory
cd $env:USERPROFILE\Documents\tools\annotator_swiss_knife

# 4. Allow script execution and run setup
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\setup\setup.ps1

# 5. Launch the application
.\scripts\run\run.ps1 gui
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### **Permission Denied (macOS/Linux)**
```bash
chmod +x scripts/setup/setup.sh
chmod +x scripts/run/run.sh
chmod +x LaunchAnnotationToolkit.command
```

#### **PowerShell Execution Policy (Windows)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **Python Not Found**
- **macOS/Linux**: Try `python3` instead of `python`
- **Windows**: Install Python from the Microsoft Store or python.org

#### **Virtual Environment Issues**
If the setup fails, try manual installation:
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### **GUI Won't Start**
Make sure you're running the GUI command:
```bash
# macOS/Linux
./scripts/run/run.sh gui

# Windows PowerShell
.\scripts\run\run.ps1 gui

# Windows Command Prompt
scripts\run\run.bat gui
```

---

## 🎯 What Each Tool Does

Once launched, you'll have access to:

- **📝 Dictionary to Bullet List**: Convert dictionaries with URLs to formatted lists
- **🧹 Text Cleaner**: Clean text from markdown/JSON/code artifacts  
- **📊 JSON Visualizer**: Format and visualize JSON data
- **💬 Conversation Visualizer**: Format conversation data

---

## 📞 Getting Help

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Verify Python installation**: `python --version` or `python3 --version`
3. **Contact the tool creator**: [Your Name] <[Your Email]>
4. **Check the main README.md** for additional documentation

---

## 🔄 Future Updates

When you receive an updated version:

1. **Backup your current folder** (if you've made any customizations)
2. **Extract the new version** to the same location
3. **Re-run the setup script** to update dependencies
4. **Launch as usual**

---

## 💡 Pro Tips

- **Create a desktop shortcut** to the run script for easy access
- **Bookmark this guide** for future reference
- **Keep the tool folder organized** in a dedicated tools directory
- **Test with sample data** to familiarize yourself with features

---

*This tool runs entirely from source code and doesn't require installation or admin privileges. It's designed to work seamlessly on Meta managed devices.*