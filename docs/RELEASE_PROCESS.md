# Release Process

This document describes how to create and publish a new release of the Annotation Toolkit.

## Overview

The project uses an automated CI/CD pipeline that builds cross-platform executables and creates GitHub Releases whenever a version tag is pushed. Version numbers are automatically derived from git tags using [setuptools-scm](https://github.com/pypa/setuptools-scm).

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: Backwards-compatible new features
- **PATCH** version: Backwards-compatible bug fixes

Examples:
- `v1.0.0` - Major release
- `v1.1.0` - Minor release (new features)
- `v1.1.1` - Patch release (bug fixes)
- `v1.0.0-beta.1` - Pre-release (beta)
- `v1.0.0-rc.1` - Release candidate

## Release Workflow

### 1. Prepare the Release

#### a. Update CHANGELOG.md

Move all items from `[Unreleased]` to a new version section:

```markdown
## [1.2.0] - 2025-01-15

### Added
- New feature XYZ

### Fixed
- Bug ABC

## [Unreleased]
<!-- Leave empty for next release -->
```

Update the version links at the bottom of CHANGELOG.md.

#### b. Ensure All Tests Pass

Run the full test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=annotation_toolkit --cov-report=term-missing
```

Check the CI status on GitHub - all workflows should be passing.

#### c. Commit Changes

```bash
git add CHANGELOG.md
git commit -m "Prepare for v1.2.0 release"
git push origin main
```

### 2. Create and Push the Tag

The tag name determines the version number for the release.

```bash
# Create an annotated tag
git tag -a v1.2.0 -m "Release version 1.2.0"

# Push the tag to GitHub
git push origin v1.2.0
```

**Important**:
- Always use the format `v{MAJOR}.{MINOR}.{PATCH}` (e.g., `v1.2.0`)
- Use annotated tags (`-a`) for better Git history
- The tag message should be brief (e.g., "Release version 1.2.0")

### 3. Automated Build Process

Once you push the tag, GitHub Actions automatically:

1. **Builds executables** for:
   - macOS (.app bundle, distributed as ZIP)
   - Windows (.exe executable)
   - Linux (standalone binary)

2. **Generates SHA256 checksums** for each artifact

3. **Creates a GitHub Release** with:
   - Release notes (auto-generated)
   - All platform executables attached
   - Checksum files for verification
   - Installation instructions

You can monitor the build progress at:
```
https://github.com/9scorp4/annotator-swiss-knife/actions
```

### 4. Review and Publish the Release

1. Go to [Releases](https://github.com/9scorp4/annotator-swiss-knife/releases)
2. Find your newly created release
3. Review the release notes and assets
4. Edit the release notes if needed to add more details
5. The release will be published automatically (not a draft)

### 5. Announce the Release

Share the release with users:

- Update the README.md if installation instructions changed
- Announce on project communication channels
- Update documentation if needed

## Pre-Release Versions

For beta, alpha, or release candidate versions:

```bash
# Beta release
git tag -a v1.2.0-beta.1 -m "Release version 1.2.0-beta.1"
git push origin v1.2.0-beta.1

# Release candidate
git tag -a v1.2.0-rc.1 -m "Release version 1.2.0-rc.1"
git push origin v1.2.0-rc.1
```

Pre-releases are automatically marked as "Pre-release" on GitHub.

## Manual Release Trigger

You can manually trigger a release build from GitHub:

1. Go to [Actions](https://github.com/9scorp4/annotator-swiss-knife/actions)
2. Select "Release" workflow
3. Click "Run workflow"
4. Enter the tag name (e.g., `v1.2.0`)
5. Click "Run workflow"

This is useful for:
- Re-building a release if something went wrong
- Testing the release process
- Creating a release for an existing tag

## Hotfix Releases

For urgent bug fixes:

1. Create a hotfix branch from the release tag:
   ```bash
   git checkout -b hotfix/1.2.1 v1.2.0
   ```

2. Make your fixes and commit:
   ```bash
   git add .
   git commit -m "Fix critical bug XYZ"
   ```

3. Update CHANGELOG.md with the hotfix

4. Merge to main and tag:
   ```bash
   git checkout main
   git merge hotfix/1.2.1
   git tag -a v1.2.1 -m "Release version 1.2.1 (hotfix)"
   git push origin main
   git push origin v1.2.1
   ```

## Troubleshooting

### Build Fails

If the automated build fails:

1. Check the [Actions](https://github.com/9scorp4/annotator-swiss-knife/actions) tab for error logs
2. Fix the issue in your code
3. Delete the tag locally and remotely:
   ```bash
   git tag -d v1.2.0
   git push origin :refs/tags/v1.2.0
   ```
4. Create the tag again after fixing

### Version Mismatch

The package version is automatically derived from the git tag. If you see version warnings:

1. Ensure setuptools-scm is installed:
   ```bash
   pip install setuptools-scm>=8.0
   ```

2. Verify the version is detected correctly:
   ```bash
   python -c "from annotation_toolkit import __version__; print(__version__)"
   ```

### Executables Not Code-Signed

Currently, executables are **not code-signed**. Users will see security warnings:

- **macOS**: Right-click the app and select "Open" to bypass Gatekeeper
- **Windows**: Click "More info" then "Run anyway" in SmartScreen
- **Linux**: Make executable with `chmod +x` before running

Code signing can be added in the future by:
1. Obtaining certificates (Apple Developer, Windows code signing)
2. Adding signing steps to the release workflow
3. Storing certificates securely in GitHub Secrets

## Release Checklist

Use this checklist for each release:

- [ ] All tests pass locally
- [ ] CI/CD workflows are green
- [ ] CHANGELOG.md is updated
- [ ] Version number follows semantic versioning
- [ ] Commit changes with descriptive message
- [ ] Create annotated tag with correct version
- [ ] Push tag to GitHub
- [ ] Monitor automated build process
- [ ] Verify artifacts are attached to release
- [ ] Review and enhance release notes
- [ ] Test downloads on each platform (if possible)
- [ ] Announce release to users

## Getting Help

If you encounter issues with the release process:

1. Check the [GitHub Actions logs](https://github.com/9scorp4/annotator-swiss-knife/actions)
2. Review this documentation
3. Check the workflow file: `.github/workflows/release.yml`
4. Open an issue on GitHub for assistance
