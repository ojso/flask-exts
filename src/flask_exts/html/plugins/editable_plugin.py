from flask import url_for
from ..plugin_base import PluginBase


class EditablePlugin(PluginBase):
    """
    Usage:
        <!-- Text field -->
        <span class="editable" data-type="text" data-name="username">
            John Doe
        </span>

        <!-- Select field -->
        <span class="editable" data-type="select" data-name="status" data-options='{"active":"Active","inactive":"Inactive"}'>
            active
        </span>

        <!-- With AJAX save -->
        <span class="editable" data-type="text" data-name="title" data-url="/api/post/1/title">
            Post Title
        </span>
    """

    def __init__(self):
        super().__init__("editable", weight=60)

    def script(self):
        s = """
        <script type="module">
        import Editable from 'url_for'
        const editor = new Editable({                
            onSuccess: (target,value, ) => {
                const toast = target.closest(".card")?.querySelector(".toast")
                if (toast) {
                toast.style.display = "block"
                setTimeout(() => { toast.style.display = "none" }, 2000)
                }
            }
        })
        </script>
        """
        return s.replace(
            "url_for", url_for("_template.static", filename="js/editable.js")
        )
