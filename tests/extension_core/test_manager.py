from flask_exts.extension_core.base import Extension
from flask_exts.extension_core.manager import ExtensionManager


class FakeApp:
    """Only provides the interface needed by ExtensionManager.init_app."""

    def __init__(self):
        self.extensions = {}


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------
def make_extension(name, dependencies=()):
    class FakeExtension(Extension):
        @property
        def name(self):
            return name

        @property
        def dependencies(self):
            return list(dependencies)

        def init_app(self, app):
            pass

    FakeExtension.__name__ = f"Fake{name.title()}Extension"
    return FakeExtension


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
def test_register_extension_documented_usage():
    """A6 regression: the documented usage `exts.register_extension(MyExtension)` must work."""
    exts = ExtensionManager(register_builtin=False)
    ext = exts.register_extension(make_extension("my_ext"))
    assert exts.get_extension("my_ext") is ext


def test_register_before_init_app_required():
    """Call register_extension before init_app; the extension is registered correctly."""
    exts = ExtensionManager(register_builtin=False)
    exts.register_extension(make_extension("a"))
    exts.init_app(FakeApp())
    assert exts.has_extension("a") is True


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
def test_init_app_registers_self_on_app():
    app = FakeApp()
    exts = ExtensionManager(register_builtin=False)
    exts.init_app(app)
    assert app.extensions["exts"] is exts


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------
def test_has_extension_forwarding():
    exts = ExtensionManager(register_builtin=False)
    exts.register_extension(make_extension("a"))
    exts.init_app(FakeApp())
    assert exts.has_extension("a") is True
    assert exts.has_extension("b") is False


# ---------------------------------------------------------------------------
# Builtin extension graph (real dependency: startup must come after admin)
# ---------------------------------------------------------------------------
def test_builtin_graph_initializes_in_valid_order():
    """The most valuable one: use the real builtin dependency graph to verify that topological sorting holds under all declarations.

    If `dependencies = ["admin"]` is not added to startup_ext, this test will fail at
    order.index("startup") > order.index("admin")—this is exactly the order described in section 17.0
    of CODE_REVIEW: "removing only priority will break".
    """
    exts = ExtensionManager()
    order = exts.get_registry().initialization_order()

    # Each extension must appear after all of its dependencies
    for name in order:
        for dep in exts.get_extension(name).dependencies:
            assert order.index(dep) < order.index(name), (
                f"'{dep}' must be initialized before '{name}', got order: {order}"
            )

    # Specific constraint: startup needs to register views with admin, so admin must be initialized first
    assert order.index("startup") > order.index("admin")


def test_startup_runs_after_admin():
    """A concrete version of test_builtin_graph, with a more direct failure message."""
    exts = ExtensionManager()
    order = exts.get_registry().initialization_order()
    assert "startup" in order and "admin" in order
    assert order.index("startup") > order.index("admin")
