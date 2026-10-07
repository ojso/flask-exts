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
        super().__init__("flatpickr", version="4.6.13")

    def style(self):
        """Load local Flatpickr CSS"""
        url = url_for(
            "_template.static", filename="vendor/flatpickr/flatpickr.min.css"
        )
        return f'<link rel="stylesheet" href="{url}">'

    def script(self):
        """Load Flatpickr JavaScript and initialization"""
        js_url = url_for(
            "_template.static", filename="vendor/flatpickr/flatpickr.min.js"
        )
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
