from collections import OrderedDict
from flask import request
from flask import flash
from flask_babel import gettext
from .filter import BaseFilter

class FilterGroup:
    def __init__(self, label):
        self.label = label
        self.filters = []

    def append(self, filter):
        self.filters.append(filter)

    def non_lazy(self):
        filters = []
        for item in self.filters:
            copy = dict(item)
            options = copy["options"]
            if options:
                copy["options"] = [(k, v) for k, v in options]
            filters.append(copy)
        return self.label, filters

    def __iter__(self):
        return iter(self.filters)


class FilterMixin:
    column_filters = None
    """
        Collection of the column filters.

        Can contain either field names or instances of :class:`~.model.filters.BaseFilter` classes.
        Can contain either field names or instances of :class:`.sqla.filters.BaseSQLAFilter` classes.

        Example::

            class MyModelView(BaseModelView):
                column_filters = ('user', 'email')

        or::

            from .sqla.filters import BooleanEqualFilter

            class MyModelView(BaseModelView):
                column_filters = (BooleanEqualFilter(column=User.name, name='Name'),)

        or::

            from .sqla.filters import BaseSQLAFilter

            class FilterLastNameBrown(BaseSQLAFilter):
                def apply(self, query, value, alias=None):
                    if value == '1':
                        return query.filter(self.column == "Brown")
                    else:
                        return query.filter(self.column != "Brown")

                def operation(self):
                    return 'is Brown'

            class MyModelView(BaseModelView):
                column_filters = [
                    FilterLastNameBrown(
                        User.last_name, 'Last Name', options=(('1', 'Yes'), ('0', 'No'))
                    )
                ]
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def init_filters(self):
        self._filters = self.get_filters()

        if self._filters:
            self._filter_groups = OrderedDict()
            self._filter_args = {}

            for i, flt in enumerate(self._filters):
                if flt.name not in self._filter_groups:
                    self._filter_groups[flt.name] = FilterGroup(flt.name)
                self._filter_groups[flt.name].append(
                    {
                        "index": i,
                        "arg": self.get_filter_arg(i, flt),
                        "operation": flt.operation(),
                        "options": flt.get_options() or None,
                        "type": flt.data_type,
                    }
                )

                self._filter_args[self.get_filter_arg(i, flt)] = (i, flt)
        else:
            self._filter_groups = None
            self._filter_args = None

    def get_filters(self):
        """
        Return a list of filter objects.
        """
        if self.column_filters:
            filters = []

            for f in self.column_filters:
                if isinstance(f, BaseFilter):
                    filters.append(f)
                else:
                    flts = self.scaffold_filters(f)
                    if flts:
                        filters.extend(flts)
                    else:
                        raise Exception("Unsupported filter type %s" % f)
            return filters
        else:
            return None

    def scaffold_filters(self, name):
        """
        Generate filter object for the given name

        :param name:
            Name of the field
        """
        return None
    
    def get_filter_arg(self, index, flt):
        """
        Given a filter `flt`, return a unique name for that filter in this view.

        Does not include the `flt[n]_` portion of the filter name.

        :param index:
            Filter index in _filters array
        :param flt:
            Filter instance
        """

        return str(index)
        
    def _get_filters(self, filters):
        """
        Get active filters as dictionary of URL arguments and values

        :param filters:
            List of filters from ViewArgs object
        """
        kwargs = {}

        if filters:
            for i, pair in enumerate(filters):
                idx, flt_name, value = pair

                key = "flt%d_%s" % (i, self.get_filter_arg(idx, self._filters[idx]))
                kwargs[key] = value

        return kwargs
    
    def _get_filter_groups(self):
        """
        Returns non-lazy version of filter strings
        """
        if self._filter_groups:
            results = OrderedDict()

            for group in self._filter_groups.values():
                key, items = group.non_lazy()
                results[key] = items

            return results

        return None
    
    # URL generation helpers
    def _get_list_filter_args(self):
        if self._filters:
            filters = []

            for arg in request.args:
                if not arg.startswith("flt"):
                    continue

                if "_" not in arg:
                    continue

                pos, key = arg[3:].split("_", 1)

                if key in self._filter_args:
                    idx, flt = self._filter_args[key]

                    value = request.args[arg]

                    if flt.validate(value):
                        data = (pos, (idx, flt.name, value))
                        filters.append(data)
                    else:
                        flash(gettext("Invalid Filter Value: %(value)s", value=value), "error")

            # Sort filters
            return [v[1] for v in sorted(filters, key=lambda n: n[0])]

        return None

    
