"""Flatpickr Plugin - Lightweight date range picker without jQuery"""

from flask import url_for
from markupsafe import Markup
from ..plugin_base import PluginBase


class FlatpickrPlugin(PluginBase):
    """
    Flatpickr is a lightweight and powerful datetimepicker with
    no dependencies.

    Features:
    - No jQuery dependency
    - Lightweight (~5KB min+gzip)
    - Date and time selection
    - Range selection
    - Bootstrap 5 compatible
    - Multiple date formats
    - Mobile-friendly

    https://flatpickr.js.org/
    """

    def __init__(self):
        super().__init__("flatpickr", weight=55)
        self.version = "4.6.13"

    def style(self):
        """Load Flatpickr CSS from CDN"""
        return f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr@{self.version}/dist/flatpickr.min.css">'

    def script(self):
        """Load Flatpickr JavaScript and initialization"""
        js_url = f"https://cdn.jsdelivr.net/npm/flatpickr@{self.version}/dist/flatpickr.min.js"
        return Markup(f"""
            <script src="{js_url}"></script>
            <script>
                // Initialize Flatpickr for date inputs
                document.addEventListener('DOMContentLoaded', function() {{
                    var dateInputs = document.querySelectorAll('input[type="date"][data-flatpickr]');
                    dateInputs.forEach(function(input) {{
                        flatpickr(input, {{
                            dateFormat: input.getAttribute('data-format') || 'Y-m-d',
                            mode: input.getAttribute('data-mode') || 'single',
                            enableTime: input.hasAttribute('data-enable-time'),
                            noCalendar: input.hasAttribute('data-no-calendar'),
                            time_24hr: true,
                            locale: 'en'
                        }});
                    }});
                }});

                // Initialize Flatpickr for date range inputs
                var rangeInputs = document.querySelectorAll('input[data-flatpickr-range]');
                if (rangeInputs.length >= 2) {{
                    flatpickr(rangeInputs, {{
                        mode: 'range',
                        dateFormat: rangeInputs[0].getAttribute('data-format') || 'Y-m-d',
                        locale: 'en'
                    }});
                }}

                // Manual initialization function
                window.initFlatpickr = function(selector, options) {{
                    return flatpickr(selector, options || {{}});
                }};
            </script>
        """)
