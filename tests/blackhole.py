class Blackhole:
    """A null object whose attribute access, calls, indexing, and iteration
    all return itself, so arbitrary chained access never raises.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        # Singleton: ensures obj.a is obj.a.b is obj.a().b
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ---------- Attribute access ----------
    def __getattr__(self, name):
        # Only invoked when normal lookup fails; won't shadow real attributes
        return self

    def __setattr__(self, name, value):
        pass

    def __delattr__(self, name):
        pass

    # ---------- Call / subscript ----------
    def __call__(self, *args, **kwargs):
        return self

    def __getitem__(self, key):
        return self

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    # ---------- Iteration / length ----------
    def __iter__(self):
        return iter(())

    def __next__(self):
        raise StopIteration

    def __len__(self):
        return 0

    def __contains__(self, item):
        return False

    # ---------- Boolean / comparison ----------
    def __bool__(self):
        return False

    def __eq__(self, other):
        return other is None or isinstance(other, Blackhole)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 0

    # ---------- String conversion ----------
    def __repr__(self):
        return "None"

    def __str__(self):
        return ""

    def __format__(self, format_spec):
        return ""

    # ---------- Type conversion ----------
    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __index__(self):
        return 0

    def __bytes__(self):
        return b""

    # ---------- Context manager ----------
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False
