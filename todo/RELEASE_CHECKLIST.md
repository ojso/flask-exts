# Release Preparation Checklist

## 📋 Pre-Release Tasks

### Version and Metadata
- [ ] Decide version number (e.g., 0.2.0)
- [ ] Update `src/flask_exts/__about__.py` with new version
- [ ] Update `README.md` with new features
- [ ] Review and finalize CHANGELOG.md
- [ ] Update project description if needed

### Code Quality
- [ ] Run all tests locally
  ```bash
  pytest tests/ -v
  ```
- [ ] Check code coverage
  ```bash
  pytest --cov=flask_exts tests/
  ```
- [ ] Run linters
  ```bash
  flake8 src/flask_exts/
  black --check src/
  isort --check-only src/
  ```
- [ ] Type checking (if applicable)
  ```bash
  mypy src/flask_exts/
  ```

### Documentation
- [ ] Verify all docs build correctly
  ```bash
  cd docs && make html
  ```
- [ ] Check for broken links in documentation
- [ ] Verify code examples in documentation work
- [ ] Review API documentation completeness
- [ ] Ensure CHANGELOG is clear and complete

### Dependencies
- [ ] Verify `pyproject.toml` is correct
  ```bash
  python -m build --sdist
  ```
- [ ] Check minimum Python version (3.10)
- [ ] Test with all supported Python versions if possible
  - Python 3.10
  - Python 3.11
  - Python 3.12
  - Python 3.13
- [ ] Verify all required dependencies are listed
- [ ] Verify optional dependencies are correct

### Security
- [ ] Run security checks
  ```bash
  pip install bandit
  bandit -r src/
  ```
- [ ] Check for vulnerable dependencies
  ```bash
  safety check
  ```
- [ ] Review CHANGELOG for security fixes

### Compatibility
- [ ] Test on Linux (primary platform)
- [ ] Test on macOS (if available)
- [ ] Test on Windows (if available)
- [ ] Test backward compatibility with example code
- [ ] Verify imports work correctly

## 🔄 Release Process

### 1. Prepare Release Commit

```bash
# Make sure everything is committed
git status

# Create release commit
git commit -m "Release version 0.2.0" --allow-empty

# Create git tag
git tag -a v0.2.0 -m "Version 0.2.0"
```

### 2. Build Distribution Packages

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build source distribution and wheel
python -m build

# Verify packages
ls -la dist/
```

### 3. Upload to PyPI (Test First)

```bash
# Test upload to TestPyPI first
twine upload --repository testpypi dist/*

# Then verify on https://test.pypi.org/project/Flask-Exts/
```

### 4. Upload to PyPI (Production)

```bash
# Upload to production PyPI
twine upload dist/*

# Verify on https://pypi.org/project/Flask-Exts/
```

### 5. Push to GitHub

```bash
# Push commits and tags
git push origin main
git push origin v0.2.0
```

## ✅ Post-Release Tasks

### Announcement
- [ ] Create GitHub release with notes
- [ ] Post announcement on project channels
- [ ] Update project website if applicable
- [ ] Notify users via email if applicable

### Monitoring
- [ ] Monitor for issues with new release
- [ ] Check download statistics
- [ ] Review any bug reports
- [ ] Create issues for follow-up items

### Next Version Preparation
- [ ] Update version to development version (e.g., 0.3.0.dev0)
- [ ] Create new section in CHANGELOG for upcoming changes
- [ ] Plan next release features

## 📦 Checklist by Component

### Flask-Exts Core
- [x] Code complete
- [x] Tests complete
- [x] Documentation complete
- [x] No breaking changes
- [x] Backward compatible

### Admin Module
- [x] CRUD operations working
- [x] Inline models functional
- [x] Filters and search operational
- [x] Export functionality ready
- [x] Tests passing

### User/Security Module
- [x] Authentication working
- [x] 2FA implemented
- [x] Permissions system operational
- [x] Tests passing

### Forms/Fields
- [x] All fields functional
- [x] Validation working
- [x] Widgets rendering correctly
- [x] Tests passing

### Templates/Themes
- [x] Bootstrap 5 compatible
- [x] Responsive design
- [x] Theme customization working
- [x] Tests passing

### Documentation
- [x] Getting Started complete
- [x] Admin tutorial complete
- [x] Advanced guides complete
- [x] API documentation complete
- [x] Migration guides complete

### Plugins
- [x] All plugins functional
- [x] Plugin system working
- [x] New JS plugins (Tom Select, Flatpickr, Day.js, Inline Edit)
- [x] Plugin documentation complete

## 🚀 Release Checklist Template

```
Release: Flask-Exts v0.2.0
Date: 2026-08-14
Release Manager: David Hua

Pre-Release
  [ ] Version updated
  [ ] CHANGELOG complete
  [ ] README updated
  [ ] Tests passing
  [ ] Docs building
  [ ] Security checks passed
  [ ] Backward compatibility verified

Build & Test
  [ ] Packages build successfully
  [ ] Test PyPI upload works
  [ ] Test installation from TestPyPI
  [ ] All imports work
  [ ] Examples run correctly

Release
  [ ] PyPI upload successful
  [ ] GitHub tag created
  [ ] GitHub release created
  [ ] Announcement posted

Post-Release
  [ ] Downloads monitoring
  [ ] Issue tracking started
  [ ] Next version planned
```

## 📝 Release Notes Template

```markdown
# Flask-Exts v0.2.0 Release

🎉 **Major Update**: Complete modernization and documentation overhaul

## Highlights

### ✨ New Features
- [List major features]

### 🐛 Bug Fixes  
- [List major fixes]

### 📚 Documentation
- [List new documentation]

### ⚡ Performance
- [Performance improvements]

## Breaking Changes
- None - fully backward compatible!

## Migration Guide
See [CHANGELOG.md](CHANGELOG.md) for detailed upgrade instructions.

## Contributors
Thanks to all who contributed to this release!

## Installation

```bash
pip install --upgrade flask-exts
```

## Links
- [Documentation](https://flask-exts.readthedocs.io)
- [GitHub](https://github.com/ojso/flask-exts)
- [Issue Tracker](https://github.com/ojso/flask-exts/issues)
```

## 🎯 Success Criteria

Before marking release as complete:

✅ All tests passing  
✅ Documentation complete  
✅ No critical bugs  
✅ Performance acceptable  
✅ Backward compatibility maintained  
✅ Package builds successfully  
✅ PyPI upload successful  
✅ GitHub release created  
✅ Announcement posted  

## 📞 Support

For release issues:
- Check GitHub Issues
- Review CHANGELOG for breaking changes
- Consult documentation
- Open new issue if problem persists
