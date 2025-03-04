from urllib.parse import urlencode
from markupsafe import Markup
from flask import current_app


RECAPTCHA_SCRIPT_DEFAULT = "https://www.google.com/recaptcha/api.js"
RECAPTCHA_DIV_CLASS_DEFAULT = "g-recaptcha"
RECAPTCHA_TEMPLATE = """
<script src='%s' async defer></script>
<div class="%s" %s></div>
"""

class RecaptchaWidget:
    def recaptcha_html(self, public_key):
        html = current_app.config.get("RECAPTCHA_HTML")
        if html:
            return Markup(html)
        params = current_app.config.get("RECAPTCHA_PARAMETERS")
        script = current_app.config.get("RECAPTCHA_SCRIPT")
        if not script:
            script = RECAPTCHA_SCRIPT_DEFAULT
        if params:
            script += "?" + urlencode(params)
        attrs = current_app.config.get("RECAPTCHA_DATA_ATTRS", {})
        attrs["sitekey"] = public_key
        snippet = " ".join(f'data-{k}="{attrs[k]}"' for k in attrs)  # noqa: B028, B907
        div_class = current_app.config.get("RECAPTCHA_DIV_CLASS")
        if not div_class:
            div_class = RECAPTCHA_DIV_CLASS_DEFAULT
        return Markup(RECAPTCHA_TEMPLATE % (script, div_class, snippet))

    def __call__(self, field, error=None, **kwargs):
        """Returns the recaptcha input HTML."""

        public_key = current_app.config["RECAPTCHA_PUBLIC_KEY"]
        return self.recaptcha_html(public_key)
