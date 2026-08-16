# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Core Framework Improvements
- ✨ Split `template/` module into independent top-level modules for better organization
  - New `forms/` module (33 files): form components, fields, validators, widgets
  - New `plugins/` module (21 files): plugin system and plugin managers
  - New `theme/` module: theme configuration and customization
  - Maintained 100% backward compatibility with old import paths

- ✨ Comprehensive documentation additions (3,400+ lines)
  - Advanced custom plugins development guide
  - Custom form fields and validators tutorial
  - Flask extension development guide
  - Performance optimization best practices
  - Theme customization guide
  - Advanced security patterns

- ✨ Bootstrap 5 + Native JavaScript migration
  - Tom Select plugin (lightweight Select2 replacement, 8KB)
  - Flatpickr plugin (lightweight date picker, 5KB)
  - Day.js plugin (lightweight date library, 2KB)
  - Inline Edit plugin (X-Editable replacement, 2KB)
  - 92% reduction in JavaScript library size (229 KB → 17 KB)
  - Complete migration guide with examples

#### Architecture Improvements
- ✨ Renamed `bootstrap/` module to `startup/` for clarity
- ✨ Restructured dependencies with optional dependency support
  - Core dependencies: Flask, WTForms, SQLAlchemy, flask-babel, Flask-Login, PyJWT
  - Optional: `export` (tablib), `security` (pyotp), `all`

#### Bug Fixes & Improvements
- 🐛 Fixed `inline_model` primary key detection
  - Changed from hardcoded `_pk = "id"` to dynamic `get_primary_key(model)`
  - Fixed variable shadowing in `populate_obj()` method
  - Removed broken `on_model_change` callback

- 🐛 Fixed naming convention violations
  - Renamed `actived` to `is_active` (preserved DB column name for compatibility)
- 🐛 Removed dead code in `admin/sqla/form.py`

#### Testing Improvements
- ✨ Complete inline_model test coverage (6 test classes)
- ✨ Authorizer and security tests
- ✨ CLI commands tests

#### Documentation
- 📚 Getting Started guide: step-by-step tutorial from zero to working app
- 📚 Admin ModelView comprehensive tutorial with examples
- 📚 Bootstrap 5 migration guide with examples
- 📚 Advanced usage guides (plugins, fields, extensions, performance, theming, security)

### Changed

#### Breaking Changes
- None (all changes maintain backward compatibility)

#### Deprecated
- None

#### Security
- 🔐 Enhanced security documentation with advanced patterns
- 🔐 OAuth2 and social login examples
- 🔐 Advanced MFA implementation patterns
- 🔐 Data encryption and GDPR compliance examples

### Fixed
- Fixed inline form functionality with correct primary key detection
- Fixed filter naming consistency across admin views
- Fixed is_active field naming for Flask conventions

### Removed
- ⚠️ jQuery dependency (now using native JavaScript)
- ⚠️ Select2 (replaced by Tom Select)
- ⚠️ daterangepicker (replaced by Flatpickr)
- ⚠️ Moment.js (replaced by Day.js)
- ⚠️ X-Editable (replaced by Inline Edit)

## [0.2.0] - 2026-08-14

### Added

#### Initial Feature Set
- Admin panel with CRUD operations
- User authentication and authorization
- Security framework (2FA, permissions, roles)
- Form components and widgets
- Template rendering system
- Plugin architecture
- Email support
- Internationalization (i18n)
- CLI commands for administration

### Features
- **Admin Views**: Comprehensive admin interface for data management
- **Authentication**: User registration, login, password reset, 2FA
- **User Center**: User profile management and account settings
- **Security**: Role-based access control, permission system
- **Forms**: Rich form components with validation
- **Widgets**: Custom Bootstrap components
- **Templates**: Jinja2 integration with macros
- **Plugins**: Extensible plugin system
- **Commands**: CLI tools for user and data management
- **Email**: Email integration for notifications
- **Babel**: Internationalization support

## Upgrading

### From 0.1 to 0.2

No breaking changes. All old import paths still work via backward compatibility proxies.

#### Optional: Update to new import paths

```python
# Old (still works)
from flask_exts.template.forms import FlaskForm
from flask_exts.template.plugins import PluginManager
from flask_exts.template import Theme

# New (recommended)
from flask_exts.forms import FlaskForm
from flask_exts.plugins import PluginManager
from flask_exts.theme import Theme
```

#### Optional: Migrate JavaScript libraries

See `docs/bootstrap5_migration.rst` for complete migration guide:

```html
<!-- Old (jQuery required) -->
<select data-toggle="select2"></select>

<!-- New (native JS) -->
<select data-tom-select></select>
```

## Contributors

- David Hua ([@ojso](https://github.com/ojso))

## License

MIT License - See LICENSE.rst for details
