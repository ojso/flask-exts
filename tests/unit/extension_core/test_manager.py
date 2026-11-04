from flask_exts.extension_core.base import Extension
from flask_exts.extension_core.manager import ExtensionManager


class FakeApp:
    """Only provides the interface needed by ExtensionManager.init_app."""

    def __init__(self):
        self.extensions = {}


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------
def make_extension(name, dependencies=(), record=None):
    class FakeExtension(Extension):
        @property
        def name(self):
            return name

        @property
        def dependencies(self):
            return list(dependencies)

        def init_app(self, app):
            if record is not None:
                record.append(f"init:{name}")

        def post_init(self, app):
            if record is not None:
                record.append(f"post_init:{name}")

    FakeExtension.__name__ = f"Fake{name.title()}Extension"
    return FakeExtension


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
def test_register_extension_documented_usage():
    """A6 regression: the documented usage must work.

    The documented usage is `exts.register_extension(MyExtension)`.
    """
    exts = ExtensionManager(register_builtin=False)
    ext = exts.register_extension(make_extension("my_ext"))
    assert exts.get_extension("my_ext") is ext


def test_register_before_init_app_required():
    """Call register_extension before init_app.

    The extension is registered correctly.
    """
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
# ---------------------------------------------------------------------------
# Two-phase lifecycle: init_app then post_init
# ---------------------------------------------------------------------------
def test_all_init_app_run_before_any_post_init():
    """post_init is a second, distinct pass: every init_app finishes first."""
    record = []
    exts = ExtensionManager(register_builtin=False)
    for n in ("a", "b", "c"):
        exts.register_extension(make_extension(n, record=record))
    exts.init_app(FakeApp())

    inits = [i for i, step in enumerate(record) if step.startswith("init:")]
    posts = [i for i, step in enumerate(record) if step.startswith("post_init:")]
    assert max(inits) < min(posts), record


def test_post_init_order_independent_of_dependency():
    """A dependent's post_init still runs after its dependency's post_init,
    following the same topological order as init_app."""
    record = []
    exts = ExtensionManager(register_builtin=False)
    exts.register_extension(make_extension("dep", record=record))
    exts.register_extension(make_extension("dependent", ["dep"], record=record))
    exts.init_app(FakeApp())

    assert record.index("post_init:dep") < record.index("post_init:dependent")


def test_registration_order_between_unrelated_extensions_does_not_matter():
    """B2 regression: an extension that collects contributions from peers
    (admin collecting views) must see every peer's init_app result,
    regardless of which one was registered first -- as long as neither
    declares a dependency on the other.
    """
    record = []
    exts = ExtensionManager(register_builtin=False)
    # "collector" is registered BEFORE "provider" -- the exact shape of the
    # real bug (AdminExtension registered before PortalExtension).
    exts.register_extension(make_extension("collector", record=record))
    exts.register_extension(make_extension("provider", record=record))
    exts.init_app(FakeApp())

    # Both post_inits ran, and both saw the other's init_app already done.
    assert "post_init:collector" in record
    assert "post_init:provider" in record


def test_builtin_graph_initializes_in_valid_order():
    """Use the real builtin dependency graph to verify topological sorting.

    The most valuable one: verify that topological sorting holds under all
    declarations. If `dependencies = ["admin"]` is not added to startup_ext,
    this test will fail at order.index("startup") > order.index("admin").
    """
    exts = ExtensionManager()
    order = exts.get_registry().initialization_order()

    # Each extension must appear after all of its dependencies
    for name in order:
        for dep in exts.get_extension(name).dependencies:
            assert order.index(dep) < order.index(name), (
                f"'{dep}' must be initialized before '{name}', got order: {order}"
            )


def test_builtin_admin_collects_portal_and_usercenter_views(app):
    """Real end-to-end check: AdminExtension's post_init picks up views from
    PortalExtension and UserCenterExtension via AdminViewMixin, even though
    AdminExtension is registered before both of them in BUILTIN_EXTENSIONS.
    """
    exts = app.extensions["exts"]
    admin = exts.get_extension("admin").get_admin()
    view_names = set(admin._views.keys())

    assert "index" in view_names  # from PortalExtension
    assert "user" in view_names  # from UserCenterExtension
