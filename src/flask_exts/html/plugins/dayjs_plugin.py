"""Day.js Plugin - Lightweight date library without Moment.js"""

from flask import url_for
from markupsafe import Markup
from ..plugin_base import PluginBase


class DayjsPlugin(PluginBase):
    """
    Day.js is a minimalist JavaScript library that parses, validates,
    manipulates, and displays dates and times for modern browsers with
    a largely Moment.js-compatible API.

    Features:
    - Lightweight (only 2KB)
    - Moment.js compatible API
    - Plugin support
    - Multiple locale support
    - No external dependencies
    - Tree-shakable

    https://day.js.org/
    """

    def __init__(self):
        super().__init__("dayjs", weight=40)
        self.version = "1.11.10"

    def script(self):
        """Load Day.js JavaScript and common plugins"""
        js_url = f'https://cdn.jsdelivr.net/npm/dayjs@{self.version}/dayjs.min.js'
        utc_plugin = f'https://cdn.jsdelivr.net/npm/dayjs@{self.version}/plugin/utc.js'
        timezone_plugin = f'https://cdn.jsdelivr.net/npm/dayjs@{self.version}/plugin/timezone.js'

        return Markup(f'''
            <script src="{js_url}"></script>
            <script src="{utc_plugin}"></script>
            <script src="{timezone_plugin}"></script>
            <script>
                // Register plugins
                dayjs.extend(window.dayjs_plugin_utc);
                dayjs.extend(window.dayjs_plugin_timezone);

                // Global dayjs alias
                window.dayjs = dayjs;

                // Common formatting utilities
                window.formatDate = function(date, format) {{
                    return dayjs(date).format(format || 'YYYY-MM-DD');
                }};

                window.formatDateTime = function(date, format) {{
                    return dayjs(date).format(format || 'YYYY-MM-DD HH:mm:ss');
                }};

                window.getDaysFromNow = function(days) {{
                    return dayjs().add(days, 'day').toDate();
                }};

                window.getRelativeTime = function(date) {{
                    var d = dayjs(date);
                    var now = dayjs();
                    var diffSeconds = now.diff(d, 'second');

                    if (diffSeconds < 60) return 'just now';
                    if (diffSeconds < 3600) return Math.floor(diffSeconds / 60) + ' minutes ago';
                    if (diffSeconds < 86400) return Math.floor(diffSeconds / 3600) + ' hours ago';
                    if (diffSeconds < 604800) return Math.floor(diffSeconds / 86400) + ' days ago';

                    return d.format('YYYY-MM-DD');
                }};
            </script>
        ''')
