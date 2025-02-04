from markupsafe import Markup


class BaseRule:
    """
    Base form rule.
    All form formatting rules should derive from `BaseRule`.
    """

    def __init__(self):
        self.parent = None
        self.rule_set = None

    def configure(self, rule_set, parent):
        """
        Configure rule and assign to rule set.

        :param rule_set:
            Rule set
        :param parent:
            Parent rule (if any)
        """
        self.parent = parent
        self.rule_set = rule_set
        return self

    @property
    def visible_fields(self):
        """
        A list of visible fields for the given rule.
        """
        return []

    def __call__(self, form, form_opts=None, field_args={}):
        """
        Render rule.

        :param form:
            Form object
        :param form_opts:
            Form options
        :param field_args:
            Optional arguments that should be passed to template or the field
        """
        raise NotImplementedError()


class BaseTextRule(BaseRule):
    """
    Render text (or HTML snippet) from string.
    """

    def __init__(self, escape=True):
        """
        Constructor.
        :param escape:
            Should text be escaped or not. Default is `True`.
        """
        super().__init__()
        self.type = "text"
        self.escape = escape

    def __markup__(self, text):
        if self.escape:
            return Markup(text)
        else:
            return text


class Text(BaseTextRule):
    """
    Render text (or HTML snippet) from string.
    """

    def __init__(self, text, escape=True):
        """
        Constructor.

        :param text:
            Text to render
        :param escape:
            Should text be escaped or not. Default is `True`.
        """
        super().__init__(escape)
        self.text = text

    def __call__(self, form, form_opts=None, field_args={}):
        return self.__markup__(self.text)


class Header(Text):
    """
    Render header text.
    """

    def __call__(self, form, form_opts=None, field_args={}):
        text = f"<h3>{self.text}</h3>"
        return self.__markup__(text)


class Field(BaseRule):
    """
    Form field rule.
    """

    def __init__(self, field_name):
        """
        Constructor.

        :param field_name:
            Field name to render
        """
        super().__init__()
        self.type = "field"
        self.field_name = field_name

    @property
    def visible_fields(self):
        return [self.field_name]

    def get_params(self, form, form_opts=None, field_args={}):
        """
        Render field.

        :param form:
            Form object
        :param form_opts:
            Form options
        :param field_args:
            Optional arguments that should be passed to template or the field
        """
        field = getattr(form, self.field_name, None)

        if field is None:
            raise ValueError("Form %s does not have field %s" % (form, self.field_name))

        opts = {}

        if form_opts:
            opts.update(form_opts.widget_args.get(self.field_name, {}))

        opts.update(field_args)
        params = {"form": form, "field": field, "kwargs": opts}

        return params


class Group(Field):
    def __init__(self, field_name, prepend=None, append=None, **kwargs):
        """
        Bootstrap Input group.
        """
        super().__init__(field_name)
        self._addons = []

        if prepend:
            if not isinstance(prepend, (tuple, list)):
                prepend = [prepend]

            for cnf in prepend:
                if isinstance(cnf, str):
                    self._addons.append({"pos": "prepend", "type": "text", "text": cnf})
                    continue

                if cnf["type"] in ("field", "html", "text"):
                    cnf["pos"] = "prepend"
                    self._addons.append(cnf)

        if append:
            if not isinstance(append, (tuple, list)):
                append = [append]

            for cnf in append:
                if isinstance(cnf, str):
                    self._addons.append({"pos": "append", "type": "text", "text": cnf})
                    continue

                if cnf["type"] in ("field", "html", "text"):
                    cnf["pos"] = "append"
                    self._addons.append(cnf)

    @property
    def visible_fields(self):
        fields = [self.field_name]
        for cnf in self._addons:
            if cnf["type"] == "field":
                fields.append(cnf["name"])
        return fields

    def get_params(self, form, form_opts=None, field_args={}):
        """
        Render field.

        :param form:
            Form object
        :param form_opts:
            Form options
        :param field_args:
            Optional arguments that should be passed to template or the field
        """
        field = getattr(form, self.field_name, None)

        if field is None:
            raise ValueError("Form %s does not have field %s" % (form, self.field_name))

        if form_opts:
            widget_args = form_opts.widget_args
        else:
            widget_args = {}

        opts = {}
        prepend = []
        append = []
        for cnf in self._addons:
            ctn = None
            typ = cnf["type"]
            if typ == "field":
                name = cnf["name"]
                fld = form._fields.get(name, None)
                if fld:
                    w_args = widget_args.setdefault(name, {})
                    if fld.type in ("BooleanField", "RadioField"):
                        w_args.setdefault("class", "form-check-input")
                    else:
                        w_args.setdefault("class", "form-control")
                    ctn = fld(**w_args)
            elif typ == "text":
                ctn = '<span class="input-group-text">%s</span>' % cnf["text"]
            elif typ == "html":
                ctn = cnf["html"]

            if ctn:
                if cnf["pos"] == "prepend":
                    prepend.append(ctn)
                else:
                    append.append(ctn)

        if prepend:
            opts["prepend"] = Markup("".join(prepend))

        if append:
            opts["append"] = Markup("".join(append))

        opts.update(widget_args.get(self.field_name, {}))
        opts.update(field_args)

        params = {"form": form, "field": field, "kwargs": opts}
        return params


class NestedRule(BaseRule):
    """
    Nested rule. Can contain child rules and render them.
    """

    def __init__(self, rules=[], separator=""):
        """
        Constructor.

        :param rules:
            Child rule list
        :param separator:
            Default separator between rules when rendering them.
        """
        super().__init__()
        self.type = "nest"
        self.rules = list(rules)
        self.separator = separator

    def configure(self, rule_set, parent):
        """
        Configure rule.

        :param rule_set:
            Rule set
        :param parent:
            Parent rule (if any)
        """
        self.rules = rule_set.configure_rules(self.rules, self)
        return super().configure(rule_set, parent)

    @property
    def visible_fields(self):
        """
        Return visible fields for all child rules.
        """
        visible_fields = []
        for rule in self.rules:
            for field in rule.visible_fields:
                visible_fields.append(field)
        return visible_fields

    def __iter__(self):
        """
        Return rules.
        """
        return self.rules


class FieldSet(NestedRule):
    """
    Field set with header.
    """

    def __init__(self, rules, header=None, separator=""):
        """
        Constructor.

        :param rules:
            Child rules
        :param header:
            Header text
        :param separator:
            Child rule separator
        """
        if header:
            rule_set = [Header(header)] + list(rules)
        else:
            rule_set = list(rules)

        super().__init__(rule_set, separator=separator)


class Row(NestedRule):
    def __init__(self, *columns, **kw):
        super().__init__(columns)
        self.type = "row"

    def __call__(self, form, form_opts=None, field_args={}):
        cols = []
        for col in self.rules:
            if col.visible_fields:
                w_args = form_opts.widget_args.setdefault(col.visible_fields[0], {})
                w_args.setdefault("column_class", "col")
            cols.append(col(form, form_opts, field_args))

        return Markup('<div class="form-row">%s</div>' % "".join(cols))


class RuleSet:
    """
    Rule set.
    """

    def __init__(self, view, rules):
        """
        Constructor.

        :param view:
            Administrative view
        :param rules:
            Rule list
        """
        self.view = view
        self.rules = self.configure_rules(rules)

    @property
    def visible_fields(self):
        visible_fields = []
        for rule in self.rules:
            for field in rule.visible_fields:
                visible_fields.append(field)
        return visible_fields

    def configure_rules(self, rules, parent=None):
        """
        Configure all rules recursively - bind them to current RuleSet and
        convert string references to `Field` rules.

        :param rules:
            Rule list
        :param parent:
            Parent rule (if any)
        """
        result = []

        for r in rules:
            if isinstance(r, str):
                result.append(Field(r).configure(self, parent))
            elif isinstance(r, (tuple, list)):
                row = Row(*r)
                result.append(row.configure(self, parent))
            else:
                try:
                    result.append(r.configure(self, parent))
                except AttributeError:
                    raise TypeError('Could not convert "%s" to rule' % repr(r))

        return result

    def __iter__(self):
        """
        Iterate through registered rules.
        """
        for r in self.rules:
            yield r
