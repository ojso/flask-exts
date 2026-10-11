from flask import url_for

from ..plugin_base import PluginBase


class ModalPlugin(PluginBase):
    def __init__(self):
        super().__init__("modal", dependencies=("bootstrap5",))

    def script(self):
        url = url_for("_template.static", filename="js/modal.js")
        return f"""<script type="module">
import ModalForm from "{url}";

document.querySelectorAll("[data-modal-form]").forEach((trigger) => {{
  trigger.addEventListener("click", () => {{
    const csrfField = trigger.dataset.csrfField || "csrf_token";
    const csrfRequired = trigger.dataset.csrfRequired !== "false";

    new ModalForm(trigger, {{
      fetchImpl: (url, init) => {{
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content?.trim();

        if (csrfRequired && !csrfToken) {{
          throw new Error("The CSRF token is missing from the page.");
        }}
        if (csrfRequired && csrfToken && typeof init.body === "string") {{
          const body = JSON.parse(init.body);
          body[csrfField] = csrfToken;
          init = {{ ...init, body: JSON.stringify(body) }};
        }}

        return fetch(url, init);
      }},
      onSuccess: () => {{
        window.location.assign(trigger.dataset.successUrl || window.location.href);
      }},
    }});
  }});
}});
</script>"""
