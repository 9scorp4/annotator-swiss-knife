# 📦 Distribution Checklist

## Choose Your Distribution Method

- **Method 1: GitHub Releases (Recommended)** - Automated, professional releases with pre-built executables
- **Method 2: Google Drive/Manual** - For team sharing when GitHub is not accessible

See [DISTRIBUTION_GUIDE.md](DISTRIBUTION_GUIDE.md) for detailed instructions on each method.

---

## Method 1: GitHub Releases Checklist

> **Recommended for**: Official releases, public distribution, version-controlled releases

### ✅ **Pre-Release Testing**

- [ ] **All tests pass locally**
  ```bash
  python -m pytest tests/
  ```

- [ ] **All tests pass in CI**
  - Check GitHub Actions status on main branch
  - Verify no failing workflows

- [ ] **Version number is correct**
  - Determine next version using semantic versioning
  - Major.Minor.Patch (e.g., v1.0.0, v1.1.0, v1.1.1)
  - Pre-release tags if needed (e.g., v1.0.0-beta.1)

### ✅ **Documentation Ready**

- [ ] **CHANGELOG.md updated**
  - Move items from `[Unreleased]` to new version section
  - Add release date
  - Update version links at bottom

- [ ] **README.md is current**
  - Installation instructions are accurate
  - Features list is up to date
  - No outdated references

### ✅ **Create the Release**

- [ ] **Commit all changes**
  ```bash
  git add .
  git commit -m "Prepare for vX.X.X release"
  git push origin main
  ```

- [ ] **Create and push the tag**
  ```bash
  git tag -a vX.X.X -m "Release version X.X.X"
  git push origin vX.X.X
  ```

- [ ] **Monitor the build**
  - Go to [Actions tab](https://github.com/9scorp4/annotator-swiss-knife/actions)
  - Watch the "Release" workflow
  - Verify all three platform builds succeed (macOS, Windows, Linux)
  - Check build artifacts are created

### ✅ **Verify the Release**

- [ ] **Check GitHub Release page**
  - Go to [Releases](https://github.com/9scorp4/annotator-swiss-knife/releases)
  - Verify release was created
  - Check all executables are attached:
    - `AnnotationToolkit-vX.X.X-macOS.zip`
    - `AnnotationToolkit-vX.X.X-Windows.exe`
    - `AnnotationToolkit-vX.X.X-Linux`
  - Verify SHA256 checksum files are present

- [ ] **Review and enhance release notes**
  - Auto-generated notes are present
  - Add any important details
  - Highlight breaking changes
  - Link to relevant documentation

- [ ] **Test downloads (if possible)**
  - Test on macOS (if available)
  - Test on Windows (if available)
  - Test on Linux (if available)
  - Verify executables run correctly

### ✅ **Post-Release**

- [ ] **Announce the release**
  - Share link to release page
  - Post in team channels if applicable
  - Update any external documentation

- [ ] **Monitor for issues**
  - Watch for user feedback
  - Check GitHub Issues for problems
  - Be ready to create hotfix if needed

---

## Method 2: Manual/Google Drive Checklist

> **Use when**: GitHub is not accessible, sharing with non-technical users, internal team distribution

### ✅ **Before You Share Your Tool**

- [ ] **Test the zip/extract process**
  ```bash
  cd /Users/ariasgarnicolas/Documents/repos
  zip -r annotator_swiss_knife.zip annotator_swiss_knife/
  # Test extraction in a different location
  ```

- [ ] **Verify setup script works on clean system**
  - [ ] Test on macOS
  - [ ] Test on Windows (if available)
  - [ ] Confirm virtual environment creation
  - [ ] Verify dependency installation

- [ ] **Test the GUI launches correctly**
  ```bash
  ./scripts/run/run.sh gui
  ```

- [ ] **Check all tools function properly**
  - [ ] Dictionary to Bullet List
  - [ ] Text Cleaner
  - [ ] JSON Visualizer
  - [ ] Conversation Visualizer

### ✅ **Documentation Ready**

- [X] **USER_SETUP_GUIDE.md** is complete and accurate
- [X] **QUICK_START_CARD.md** has correct commands
- [ ] **README.md** mentions corporate device compatibility
- [ ] All file paths in documentation are correct

### ✅ **Files to Include in Distribution**

Essential files (must include):
- [ ] Entire `annotator_swiss_knife/` folder
- [ ] `USER_SETUP_GUIDE.md`
- [ ] `QUICK_START_CARD.md`
- [ ] `README.md`
- [ ] `requirements.txt`
- [ ] All scripts in `scripts/` folder

Optional but recommended:
- [ ] `DISTRIBUTION_GUIDE.md` (for other distributors)
- [ ] `tests/` folder (for developers)
- [ ] `docs/` folder (additional documentation)

### ✅ **Distribution Package**

- [ ] **Create the zip file**:
  ```bash
  cd /Users/ariasgarnicolas/Documents/repos
  zip -r annotator_swiss_knife_v0.2.0.zip annotator_swiss_knife/
  ```

- [ ] **Test the zip file**:
  - [ ] Extract to temporary location
  - [ ] Run setup script
  - [ ] Launch GUI
  - [ ] Test one tool function

- [ ] **Verify file size is reasonable** (should be < 50MB)

### ✅ **Sharing Method**

Choose your distribution method:
- [ ] **SharePoint/OneDrive** (enterprise cloud storage)
- [ ] **Google Drive** (if available)
- [ ] **Workplace post** with file attachment
- [ ] **Email** (for small teams)
- [ ] **Ask manager** to create repository

### ✅ **User Instructions**

- [ ] **Create clear sharing message**:
  ```
  Subject: Annotation Swiss Knife - Data Processing Tool

  Hi team,

  I've created a simple annotation toolkit that might be useful for our data processing tasks. 

  📥 Download: [link to zip file]
  📖 Setup Guide: See USER_SETUP_GUIDE.md in the zip
  🚀 Quick Start: See QUICK_START_CARD.md for commands

  Features:
  - Dictionary to Bullet List conversion
  - Text cleaning from markdown/JSON
  - JSON visualization and formatting
  - Conversation data formatting

  Setup is simple - just extract and run one setup script!

  Let me know if you have questions or feedback.

  Best,
  [Your Name]
  ```

- [ ] **Include troubleshooting contact info**
- [ ] **Mention it works on corporate managed devices**

### ✅ **Post-Distribution**

- [ ] **Monitor for user feedback**
- [ ] **Be available for initial support questions**
- [ ] **Document common issues** for future versions
- [ ] **Consider creating FAQ** based on user questions

### ✅ **Version Control**

- [ ] **Tag current version** in your local repo
- [ ] **Keep backup** of distributed version
- [ ] **Document changes** for future updates
- [ ] **Plan update distribution method**

---

## 🎯 **Quick Command Reference**

### GitHub Releases (Automated)

```bash
# Update CHANGELOG.md first, then:

# Commit changes
git add .
git commit -m "Prepare for v1.0.0 release"
git push origin main

# Create and push tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Monitor build at: https://github.com/9scorp4/annotator-swiss-knife/actions
```

### Manual Distribution (Google Drive/ZIP)

```bash
# Create distribution package
cd /Users/ariasgarnicolas/Documents/repos
zip -r annotator_swiss_knife_v1.0.0.zip annotator_swiss_knife/

# Test extraction (in different location)
cd ~/Desktop
unzip ~/Documents/repos/annotator_swiss_knife_v1.0.0.zip
cd annotator_swiss_knife
./scripts/setup/setup.sh
./scripts/run/run.sh gui
```

---

## 📞 **Support Strategy**

**Be prepared to help with:**
- Python installation issues
- Permission problems on macOS
- PowerShell execution policy on Windows
- Virtual environment creation failures
- GUI launch problems

**Have ready:**
- Links to Python installation guides
- Common troubleshooting commands
- Alternative manual setup instructions

---

*✅ Once you've checked all items, your tool is ready to share!*