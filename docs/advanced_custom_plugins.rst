Custom Plugins Development
============================

English / 中文
----------------
This page is provided in English with a Chinese summary for easier reading.
中文说明：本页面保留英文原文，并附带中文说明，便于中英文对照阅读。


Flask-Exts provides a powerful plugin system that allows you to create custom plugins to extend functionality.

Understanding the Plugin System
--------------------------------

The plugin system is built on the ``PluginBase`` class which uses Python's ``__init_subclass__`` hook for automatic registration.

Basic Plugin Structure
~~~~~~~~~~~~~~~~~~~~~~~

To create a custom plugin, inherit from ``PluginBase``::

    from flask_exts.plugins import PluginBase

    class MyCustomPlugin(PluginBase):
        name = "my_custom_plugin"
        priority = 100  # Lower = higher priority

        def init_app(self, app):
            """Initialize the plugin with the Flask application"""
            pass

        def load_css(self):
            """Return CSS links or tags"""
            return []

        def load_js(self):
            """Return JavaScript code"""
            return ""

Complete Plugin Example
~~~~~~~~~~~~~~~~~~~~~~~

Here's a complete example of a custom notification plugin::

    from flask_exts.plugins import PluginBase
    from markupsafe import Markup

    class ToastNotificationPlugin(PluginBase):
        name = "toast_notification"
        priority = 50

        def init_app(self, app):
            """Initialize plugin"""
            self.app = app

        def load_css(self):
            """Load Toast.js CSS"""
            return [
                '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css">'
            ]

        def load_js(self):
            """Load Toast.js JavaScript and initialization"""
            return '''
                <script src="https://cdn.jsdelivr.net/npm/toastify-js"></script>
                <script>
                    function showToast(message, type='info') {
                        Toastify({
                            text: message,
                            className: 'toast-' + type,
                            gravity: "top",
                            position: "right",
                            duration: 3000
                        }).showToast();
                    }
                </script>
            '''

Plugin Lifecycle
~~~~~~~~~~~~~~~~

1. **Registration**: Plugin is automatically registered when class is defined
2. **Initialization**: ``init_app()`` is called during Flask app initialization
3. **Loading**: CSS/JS is loaded in template rendering
4. **Rendering**: Plugin content is included in HTML output

Advanced Plugin Techniques
---------------------------

Conditional Loading
~~~~~~~~~~~~~~~~~~~~

Load plugins only when specific conditions are met::

    class ConditionalPlugin(PluginBase):
        name = "conditional"

        def init_app(self, app):
            # Only enable in production
            self.enabled = app.config.get('ENV') == 'production'

        def load_js(self):
            if not self.enabled:
                return ""
            return "// Plugin code"

Plugin Dependencies
~~~~~~~~~~~~~~~~~~~

Handle dependencies between plugins::

    class DependentPlugin(PluginBase):
        name = "dependent_plugin"
        depends_on = ["jquery_plugin", "bootstrap5_plugin"]

        def init_app(self, app):
            # Verify dependencies are loaded
            enabled_plugins = self.get_enabled_plugins()
            for dep in self.depends_on:
                if dep not in enabled_plugins:
                    raise RuntimeError(f"Plugin {dep} is required but not loaded")

Configuration-Driven Plugins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make plugins configurable::

    class ConfigurablePlugin(PluginBase):
        name = "configurable"

        def init_app(self, app):
            self.config = app.config.get('CUSTOM_PLUGIN_CONFIG', {})
            self.theme = self.config.get('theme', 'light')
            self.animation = self.config.get('animation', True)

Plugin Integration with Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make plugins accessible in templates::

    from flask import render_template_string

    class TemplatePlugin(PluginBase):
        name = "template_plugin"

        def init_app(self, app):
            @app.context_processor
            def inject_plugin():
                return {
                    'show_widget': self.render_widget
                }

        def render_widget(self):
            return Markup('<div class="custom-widget">...</div>')

Using Custom Plugins
--------------------

Registration
~~~~~~~~~~~~

Custom plugins are automatically discovered and registered. To use them::

    from flask import Flask
    from my_plugins import ToastNotificationPlugin  # Auto-registered

    app = Flask(__name__)
    exts = ExtensionManager(app)

    # Plugin is now active and loaded in templates

Enabling/Disabling Plugins
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Control plugin loading::

    from flask_exts import Exts, get_exts

    app = Flask(__name__)
    exts = ExtensionManager(app)

    # Enable specific plugins
    template = get_exts()._template
    template.plugin_manager.enable_plugin(['bootstrap5_plugin', 'select2_plugin'])

Plugin Priority System
~~~~~~~~~~~~~~~~~~~~~~

Lower priority values load first::

    # These plugins load in order: base_plugin (0) → jquery_plugin (10) → app_plugin (50)
    PluginBase._plugins = {
        'base_plugin': (BasePlugin, 0),
        'jquery_plugin': (JQueryPlugin, 10),
        'app_plugin': (AppPlugin, 50),
    }

Best Practices
--------------

1. **Keep plugins small and focused**: Each plugin should do one thing well
2. **Use lazy loading**: Only load CSS/JS when needed
3. **Minimize dependencies**: Reduce coupling between plugins
4. **Document clearly**: Provide usage examples and configuration options
5. **Test thoroughly**: Include plugin tests in your test suite
6. **Handle errors gracefully**: Don't break the app if plugin fails
7. **Use proper priorities**: Ensure plugins load in correct order
8. **Follow naming conventions**: Use descriptive names (e.g., ``markdown_editor_plugin``)

Common Plugin Use Cases
-----------------------

- **Rich text editors** (TinyMCE, CKEditor, Quill)
- **Code editors** (Monaco, CodeMirror, Ace)
- **Data visualization** (Chart.js, D3, ECharts)
- **Notifications** (Toast.js, SweetAlert2, Notify.js)
- **UI frameworks** (Alpine.js, htmx, Petite Vue)
- **Analytics** (Google Analytics, Mixpanel, Segment)
- **CDN loading** (Font Awesome, Bootstrap Icons, Google Fonts)
- **Development tools** (Vue DevTools, React DevTools)

Troubleshooting
---------------

Plugin not loading
~~~~~~~~~~~~~~~~~~

- Check if plugin class is imported
- Verify plugin name is correct
- Check plugin priority order
- Review ``enable_plugin()`` calls

CSS/JS not appearing
~~~~~~~~~~~~~~~~~~~~

- Check ``load_css()`` and ``load_js()`` methods
- Verify return values are correct
- Check browser console for errors
- Verify template includes plugin outputs

Plugin conflicts
~~~~~~~~~~~~~~~~

- Check for duplicate plugin names
- Adjust priority values
- Review plugin dependencies
- Check for global namespace conflicts

See Also
--------

- :doc:`api` - Plugin API reference
- :doc:`getting_started` - Flask-Exts basics
- ``flask_exts.plugins`` - Plugin module source
