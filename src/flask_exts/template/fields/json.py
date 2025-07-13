import json
from wtforms.fields import TextAreaField

class JSONField(TextAreaField):
    def process_formdata(self, valuelist):
        if valuelist:
            if not valuelist[0]:
                self.data = None
                return
            try:
                self.data = json.loads(valuelist[0])
            except ValueError:
                raise ValueError(self.gettext("Invalid JSON"))

    def _value(self):
        if self.data:
            return json.dumps(self.data, ensure_ascii=False)
        else:
            return ""
