from flask import url_for
from markupsafe import Markup
from ..plugin_base import PluginBase


class TomSelectPlugin(PluginBase):
    """
    Tom Select is a lightweight and flexible select UI control
    replacement for select boxes with support for searching, remote data sets,
    and infinite scrolling of results.

    Features:
    - No jQuery dependency
    - Lightweight (~8KB min+gzip)
    - Bootstrap 5 native styling
    - Search and filtering
    - Async data loading
    - Custom rendering

    https://tom-select.js.org/
    """

    def __init__(self):
        super().__init__("tom_select", weight=50)
        self.version = "2.6.2"

    def load_css(self):
        return url_for(
            "_template.static", filename="vendor/tom-select/tom-select.default.min.css"
        )
        # return [
        #     f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tom-select@{self.version}/dist/css/tom-select.bootstrap5.min.css">'
        # ]

    def load_js(self):
        """Load Tom Select JavaScript and initialization"""
        return url_for(
            "_template.static", filename="vendor/tom-select/tom-select.complete.min.js"
        )

        return Markup(f"""
            <script src="{js_url}"></script>
            <script>
                // Auto-initialize Tom Select for select elements with data-tom-select
                document.addEventListener('DOMContentLoaded', function() {{
                    var selectElements = document.querySelectorAll('select[data-tom-select]');
                    selectElements.forEach(function(element) {{
                        if (!element.tomSelect) {{
                            new TomSelect(element, {{
                                create: element.hasAttribute('data-tom-select-create'),
                                placeholder: element.getAttribute('data-placeholder') || element.placeholder,
                                maxItems: element.multiple ? null : 1,
                                searchField: 'label',
                                labelField: 'label',
                                valueField: 'value'
                            }});
                        }}
                    }});
                }});

                // Function to manually initialize Tom Select
                window.initTomSelect = function(selector, options) {{
                    var element = document.querySelector(selector);
                    if (element && !element.tomSelect) {{
                        return new TomSelect(element, options || {{}});
                    }}
                    return element ? element.tomSelect : null;
                }};
            </script>
        """)
