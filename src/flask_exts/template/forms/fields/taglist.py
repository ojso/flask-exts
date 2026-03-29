from wtforms.fields import StringField

class TagListField(StringField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(",")]

    def _value(self):
        return ",".join(self.data) if self.data is not None else ""
