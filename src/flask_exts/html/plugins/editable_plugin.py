from flask import url_for
from ..plugin_base import PluginBase


class EditablePlugin(PluginBase):
    """
    Usage:
        <!-- Text field -->
        <span class="editable" data-type="text" data-name="username">
            John Doe
        </span>

        <!-- With AJAX save -->
        <span class="editable" data-type="text" data-id="1" data-name="title" data-url="/api/post/">
            Post Title
        </span>

        <!-- Select field -->
        <span class="editable" data-type="select" data-name="status" data-options="Active|active,Inactive|inactive">
            Active
        </span>

        <!-- Select field with json options -->
        <span class="editable" data-type="select" data-name="status"
          data-options='[{"label":"Active","value":"active"},{"label":"Inactive","value":"inactive"}]'>
          Active
        </span>
    """

    def __init__(self):
        super().__init__("editable", weight=60)

    def style(self):
        url = url_for("_template.static", filename="css/editable.css")
        return f'<link rel="stylesheet" href="{url}">'

    def script(self):
        s = """
        <script type="module">
        import Editable from '%(url_editable)s'
        import { createToast } from '%(url_ui)s'
        const editor = new Editable({                
            onSuccess: (target,value, ) => {
                const toast = createToast("saving with ${value} ok!")
                const bsToast = new bootstrap.Toast(toast, { delay:500000 });
                bsToast.show();
                toast.addEventListener('hidden.bs.toast', function () {
                    toast.remove();
                //   if (container.children.length === 0) container.remove();
                });
            }
        })
        </script>
        """
        return s % {
            "url_editable": url_for("_template.static", filename="js/editable.js"),
            "url_ui": url_for("_template.static", filename="js/ui-factory.js"),
        }
