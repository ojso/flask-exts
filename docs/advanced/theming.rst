Theme Customization Guide
==========================

English / 中文
----------------
This page is provided in English with a Chinese summary for easier reading.
中文说明：本页面保留英文原文，并附带中文说明，便于中英文对照阅读。


Learn how to customize the look and feel of your Flask-Exts application through theming.

Theme System Overview
---------------------

Flask-Exts includes a flexible theme system that allows you to customize colors, fonts, layouts, and components.

Theme Architecture
~~~~~~~~~~~~~~~~~~~

The theme system consists of:

1. **Theme class**: Manages theme configuration
2. **CSS variables**: Define theme colors and sizes
3. **Template overrides**: Customize HTML structure
4. **Template tags**: Render components with theme styling

Accessing the Theme
~~~~~~~~~~~~~~~~~~~

Access theme configuration in your application::

    from flask_exts import ExtensionManager

    exts = ExtensionManager(app)
    theme = exts.theme

    # Get theme properties
    print(theme.name)                    # 'bootstrap5'
    print(theme.form_group_class)        # 'mb-3'
    print(theme.btn_style)               # 'primary'
    print(theme.icon_size)               # '1em'

Configuring the Theme
---------------------

Application Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

Set theme in application config::

    app.config['THEME_NAME'] = 'bootstrap5'
    app.config['THEME_PRIMARY_COLOR'] = '#007bff'
    app.config['THEME_SECONDARY_COLOR'] = '#6c757d'

    exts = ExtensionManager(app)
    # Theme configuration is applied

CSS Variables
~~~~~~~~~~~~~

Flask-Exts exposes theme colors as CSS variables::

    <style>
        :root {
            --theme-primary: #007bff;
            --theme-secondary: #6c757d;
            --theme-success: #28a745;
            --theme-danger: #dc3545;
            --theme-warning: #ffc107;
            --theme-info: #17a2b8;
            --theme-light: #f8f9fa;
            --theme-dark: #343a40;
        }
    </style>

Using CSS variables in your stylesheets::

    .btn-primary {
        background-color: var(--theme-primary);
        border-color: var(--theme-primary);
    }

    .alert-danger {
        background-color: var(--theme-danger);
        color: white;
    }

Customizing Templates
---------------------

Template Override Directory Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create custom templates in your application::

    templates/
    └── admin/
        ├── master.html          # Override admin base template
        ├── model/
        │   ├── list.html        # Override list view
        │   ├── edit.html        # Override edit view
        │   └── details.html     # Override details view
        └── macros/
            ├── menu.html        # Override menu macro
            └── form.html        # Override form rendering

Overriding Admin Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~

Create custom admin master template::

    <!-- templates/admin/master.html -->
    {% extends "admin/base.html" %}

    {% block branding %}
    <a href="/admin" class="navbar-brand">
        <span class="logo">My Custom Admin</span>
    </a>
    {% endblock %}

    {% block menu %}
    <nav class="sidebar">
        {% include "admin/macros/menu.html" %}
    </nav>
    {% endblock %}

Overriding Macros
~~~~~~~~~~~~~~~~~

Create custom form macros::

    <!-- templates/admin/macros/form.html -->
    {% macro render_form(form, view) %}
        {% for field in form %}
            {% if field.type != 'HiddenField' %}
                <div class="form-group">
                    {{ field.label(class_="form-label") }}
                    {% if field.widget.input_type == 'hidden' %}
                        {{ field() }}
                    {% elif field.widget.input_type == 'textarea' %}
                        {{ field(class_="form-control", rows=5) }}
                    {% else %}
                        {{ field(class_="form-control") }}
                    {% endif %}
                    {% if field.errors %}
                        <div class="invalid-feedback">
                            {{ field.errors[0] }}
                        </div>
                    {% endif %}
                </div>
            {% endif %}
        {% endfor %}
    {% endmacro %}

Advanced Theme Customization
-----------------------------

Creating a Custom Theme Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extend the Theme class for custom behavior::

    from flask_exts.theme import Theme

    class MyCustomTheme(Theme):
        name = "custom"
        form_group_class = "custom-form-group"
        btn_style = "custom"
        icon_size = "1.5em"

        def __init__(self, name="custom"):
            super().__init__(name)
            self.custom_color_palette = {}

        def set_color_palette(self, palette):
            """Set custom color palette"""
            self.custom_color_palette = palette

        def get_css_variables(self):
            """Generate CSS variables from palette"""
            css = ":root {\n"
            for color_name, color_value in self.custom_color_palette.items():
                css += f"    --theme-{color_name}: {color_value};\n"
            css += "}"
            return css

Using Custom Theme
^^^^^^^^^^^^^^^^^^^

::

    from myapp.themes import MyCustomTheme

    app = Flask(__name__)
    exts = ExtensionManager(app)

    # Replace default theme
    exts.theme = MyCustomTheme()
    exts.theme.set_color_palette({
        'primary': '#ff6b6b',
        'secondary': '#4ecdc4',
        'accent': '#f7dc6f',
    })

Dynamic Theme Switching
~~~~~~~~~~~~~~~~~~~~~~~

Allow users to switch themes::

    @app.route('/theme/<name>')
    def set_theme(name):
        valid_themes = ['light', 'dark', 'blue']
        if name not in valid_themes:
            return 'Invalid theme', 400

        session['theme'] = name
        flash(f'Theme changed to {name}')
        return redirect(request.referrer or '/')

    @app.context_processor
    def inject_theme():
        theme_name = session.get('theme', 'light')
        return {'current_theme': theme_name}

Light and Dark Themes
~~~~~~~~~~~~~~~~~~~~~

Implement light/dark mode::

    <!-- templates/base.html -->
    {% set theme = current_theme %}
    <html data-theme="{{ theme }}">
    <head>
        <style>
            [data-theme="light"] {
                --bg-color: #ffffff;
                --text-color: #000000;
                --border-color: #e0e0e0;
            }
            [data-theme="dark"] {
                --bg-color: #1e1e1e;
                --text-color: #ffffff;
                --border-color: #404040;
            }
        </style>
    </head>
    <body style="background-color: var(--bg-color); color: var(--text-color);">
        ...
    </body>
    </html>

Theme Configuration Examples
-----------------------------

Bootstrap 5 Custom Theme
~~~~~~~~~~~~~~~~~~~~~~~~

::

    # config.py
    THEME_NAME = 'bootstrap5'
    THEME_PRIMARY_COLOR = '#007bff'
    THEME_SECONDARY_COLOR = '#6c757d'
    THEME_SUCCESS_COLOR = '#28a745'
    THEME_DANGER_COLOR = '#dc3545'
    THEME_WARNING_COLOR = '#ffc107'
    THEME_INFO_COLOR = '#17a2b8'

    # Customize Bootstrap classes
    FORM_GROUP_CLASS = 'mb-3'
    BUTTON_SIZE = 'md'
    BUTTON_STYLE = 'primary'

Material Design Theme
~~~~~~~~~~~~~~~~~~~~~

::

    THEME_NAME = 'material'
    THEME_PRIMARY_COLOR = '#3f51b5'
    THEME_ACCENT_COLOR = '#ff4081'

    # Material design specific
    MATERIAL_ELEVATION = 2
    MATERIAL_RIPPLE = True

Tailwind CSS Theme
~~~~~~~~~~~~~~~~~~

::

    THEME_NAME = 'tailwind'

    # Tailwind color palette
    THEME_COLORS = {
        'primary': 'indigo-600',
        'secondary': 'slate-600',
        'success': 'emerald-600',
        'danger': 'red-600',
    }

Practical Theme Examples
------------------------

Corporate Theme
~~~~~~~~~~~~~~~~

::

    class CorporateTheme(Theme):
        name = "corporate"
        btn_style = "corporate"
        form_group_class = "mb-4"

        colors = {
            'primary': '#1a1a2e',    # Dark navy
            'accent': '#e94560',      # Red accent
            'light': '#f0f0f0',       # Light gray
        }

    # templates/corporate/header.html
    <header class="corporate-header">
        <nav class="navbar navbar-corporate">
            <div class="container">
                <a href="/" class="navbar-brand">
                    <img src="/static/logo-corporate.svg" alt="Logo">
                </a>
                <ul class="nav navbar-nav">
                    <li><a href="/about">About</a></li>
                    <li><a href="/services">Services</a></li>
                    <li><a href="/contact">Contact</a></li>
                </ul>
            </div>
        </nav>
    </header>

Creative Agency Theme
~~~~~~~~~~~~~~~~~~~~~

::

    class CreativeTheme(Theme):
        name = "creative"
        btn_style = "rounded"
        form_group_class = "form-group-creative"

        colors = {
            'primary': '#ff6b9d',
            'accent': '#c44569',
            'light': '#ffecd2',
        }

SaaS Theme
~~~~~~~~~~

::

    class SaasTheme(Theme):
        name = "saas"
        btn_style = "gradient"
        form_group_class = "form-group-modern"

        colors = {
            'primary': '#667eea',
            'accent': '#764ba2',
            'success': '#48bb78',
        }

Best Practices
--------------

1. **Keep themes organized**: Use clear directory structure
2. **Use CSS variables**: Make themes easily customizable
3. **Provide defaults**: Ensure good default styling
4. **Test across browsers**: Verify theme works in all browsers
5. **Document customization**: Explain how to customize
6. **Minimize overrides**: Only override what you need to change
7. **Use semantic colors**: Use meaningful color names
8. **Ensure accessibility**: Maintain color contrast ratios
9. **Support dark mode**: Provide light and dark variants
10. **Version themes**: Track theme changes

Theme Migration
---------------

Migrating Between Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When upgrading Flask-Exts, update your themes::

    # From v0.1 to v0.2
    # Old CSS class: 'form-group'
    # New CSS class: 'mb-3'

    # Update your overrides accordingly
    <div class="mb-3">  <!-- Updated from 'form-group' -->
        {{ field.label }}
        {{ field }}
    </div>

See Also
--------

- :doc:`modelview` - Admin customization
- :doc:`custom_fields` - Field theming
- `Bootstrap 5 Customization <https://getbootstrap.com/docs/5.0/customize/overview/>`_
- ``flask_exts.theme`` - Theme module source
