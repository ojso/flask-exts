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
