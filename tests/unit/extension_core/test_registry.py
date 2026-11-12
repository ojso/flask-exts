import pytest

from flask_exts.extension_core.base import (
    Extension,
    ExtensionDependencyError,
    ExtensionError,
    ExtensionInitError,
    ExtensionNotFoundError,
)
from flask_exts.extension_core.registry import ExtensionRegistry


# ---------------------------------------------------------------------------
# Test helper: build a fake extension that only records init_app / shutdown call order
# ---------------------------------------------------------------------------
def make_extension(name, dependencies=(), record=None, shutdown_error=None):
    """Build a configurable fake extension.

    - record: if given a list, append(name) on init_app, append(f"post_init:{name}")
      on post_init, and append(f"shutdown:{name}") on shutdown
    - shutdown_error: if given an exception, raise it on shutdown (used to test
      exception isolation)
    """

    class FakeExtension(Extension):
        @property
        def name(self):
            return name

        @property
        def dependencies(self):
            return list(dependencies)

        def init_app(self, app):
            if record is not None:
                record.append(name)

        def post_init(self, app):
            if record is not None:
                record.append(f"post_init:{name}")

        def shutdown(self):
            if shutdown_error is not None:
                raise shutdown_error
            if record is not None:
                record.append(f"shutdown:{name}")

    FakeExtension.__name__ = f"Fake{name.title()}Extension"
    return FakeExtension


@pytest.fixture
def registry():
    return ExtensionRegistry()


# ---------------------------------------------------------------------------
# Ordering
# ---------------------------------------------------------------------------
def test_dependency_initialized_before_dependent(registry):
    """The dependent must always be ordered after the dependency.

    This is the regression test for B1.
    """
    record = []
    a = make_extension("a", dependencies=["b"], record=record)
    b = make_extension("b", record=record)
    registry.register(a)
    registry.register(b)

    assert registry.initialization_order() == ["b", "a"]

    registry.init_all(None)
    assert record == ["b", "a"]


def test_independent_extensions_keep_registration_order(registry):
    """Independent extensions keep registration order.

    This is an implicit contract that needs to be locked down.
    """
    record = []
    registry.register(make_extension("a", record=record))
    registry.register(make_extension("b", record=record))
    registry.register(make_extension("c", record=record))

    assert registry.initialization_order() == ["a", "b", "c"]
    registry.init_all(None)
    assert record == ["a", "b", "c"]


def test_deep_chain(registry):
    """c depends on b, b depends on a -> order a, b, c."""
    registry.register(make_extension("c", dependencies=["b"]))
    registry.register(make_extension("b", dependencies=["a"]))
    registry.register(make_extension("a"))

    assert registry.initialization_order() == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# Errors and edge cases
# ---------------------------------------------------------------------------
def test_missing_dependency_raises(registry):
    """Declared an unregistered dependency -> ExtensionNotFoundError."""
    registry.register(make_extension("a", dependencies=["ghost"]))
    with pytest.raises(ExtensionNotFoundError, match="ghost"):
        registry.initialization_order()


def test_circular_dependency_raises_with_cycle(registry):
    """A->B->A cycle -> ExtensionDependencyError.

    The message must contain the full cycle path.
    """
    registry.register(make_extension("a", dependencies=["b"]))
    registry.register(make_extension("b", dependencies=["a"]))
    with pytest.raises(ExtensionDependencyError, match="a -> b -> a"):
        registry.initialization_order()


def test_self_dependency_raises(registry):
    """An extension depending on itself -> also a cycle."""
    registry.register(make_extension("a", dependencies=["a"]))
    with pytest.raises(ExtensionDependencyError):
        registry.initialization_order()


def test_register_duplicate_name_raises_actionable_message(registry):
    """A6: duplicate registration must give an actionable message."""
    registry.register(make_extension("a"))
    with pytest.raises(ExtensionError, match="Duplicate name"):
        registry.register(make_extension("a", dependencies=["b"]))


def test_register_rejects_non_extension(registry):
    """Not an Extension subclass -> ExtensionError."""

    class NotAnExtension:
        pass

    with pytest.raises(ExtensionError):
        registry.register(NotAnExtension)


@pytest.mark.parametrize("bad_name", ["", "has space", "has-dash", "名字"])
def test_register_validates_name(registry, bad_name):
    """Empty name / spaces / hyphen / non-ascii -> ExtensionError."""
    with pytest.raises(ExtensionError):
        registry.register(make_extension(bad_name))


# ---------------------------------------------------------------------------
# unregister
# ---------------------------------------------------------------------------
def test_unregister(registry):
    """unregister deletes idempotently."""
    registry.register(make_extension("a"))
    assert registry.unregister("a") is True
    assert registry.unregister("a") is False
    assert registry.get_extension("a") is None


# ---------------------------------------------------------------------------
# Initialization / shutdown
# ---------------------------------------------------------------------------
def test_init_is_idempotent(registry):
    """Calling init_all twice triggers init_app only once."""
    record = []
    registry.register(make_extension("a", record=record))
    registry.register(make_extension("b", record=record))

    registry.init_all(None)
    registry.init_all(None)
    assert record == ["a", "b"]


def test_post_init_is_idempotent(registry):
    """Calling post_init_all twice triggers post_init only once per extension.

    Regression: AdminExtension.post_init registers views on each call: a
    duplicate call would raise on re-registering the same view name.
    """
    record = []
    registry.register(make_extension("a", record=record))
    registry.register(make_extension("b", record=record))
    registry.init_all(None)

    registry.post_init_all(None)
    registry.post_init_all(None)
    assert record.count("post_init:a") == 1
    assert record.count("post_init:b") == 1


def test_post_init_requires_init_first(registry):
    """post_init on an extension whose init_app has not run raises."""
    registry.register(make_extension("a"))
    with pytest.raises(ExtensionInitError):
        registry.post_init("a", None)


def test_post_init_unknown_extension_raises(registry):
    with pytest.raises(ExtensionNotFoundError):
        registry.post_init("ghost", None)


def test_post_init_follows_dependency_order(registry):
    """post_init respects the same topological order as init_app."""
    record = []
    registry.register(make_extension("dependent", dependencies=["dep"], record=record))
    registry.register(make_extension("dep", record=record))
    registry.init_all(None)
    registry.post_init_all(None)

    assert record.index("post_init:dep") < record.index("post_init:dependent")


def test_is_post_initialized(registry):
    registry.register(make_extension("a"))
    assert registry.is_post_initialized("a") is False
    registry.init_all(None)
    assert registry.is_post_initialized("a") is False
    registry.post_init_all(None)
    assert registry.is_post_initialized("a") is True


def test_shutdown_resets_post_init_state(registry):
    """A->shutdown->re-init cycle must re-run post_init, not skip it."""
    record = []
    registry.register(make_extension("a", record=record))
    registry.init_all(None)
    registry.post_init_all(None)
    registry.shutdown_all()

    assert registry.is_post_initialized("a") is False

    registry.init_all(None)
    registry.post_init_all(None)
    assert record.count("post_init:a") == 2


def test_unregister_clears_post_init_state(registry):
    registry.register(make_extension("a"))
    registry.init_all(None)
    registry.post_init_all(None)
    assert registry.is_post_initialized("a") is True

    registry.unregister("a")
    assert registry.is_post_initialized("a") is False


def test_init_failure_raises_and_marks(registry):
    class Boom(Extension):
        @property
        def name(self):
            return "boom"

        def init_app(self, app):
            raise ValueError("nope")

    registry.register(Boom)
    with pytest.raises(ValueError, match="nope"):
        registry.init_all(None)


def test_shutdown_reverse_order(registry):
    """shutdown is in reverse initialization order."""
    record = []
    registry.register(make_extension("a", record=record))
    registry.register(make_extension("b", record=record))
    registry.init_all(None)

    registry.shutdown_all()
    # Reverse initialization order -> shutdown:b before shutdown:a
    assert "shutdown:a" in record and "shutdown:b" in record
    assert record.index("shutdown:b") < record.index("shutdown:a")


def test_shutdown_exception_is_isolated(registry):
    """A failing shutdown is isolated and the remaining extensions still close."""
    record = []
    registry.register(make_extension("a", record=record))
    registry.register(
        make_extension("b", record=record, shutdown_error=ValueError("boom"))
    )
    registry.register(make_extension("c", record=record))
    registry.init_all(None)

    with pytest.warns(UserWarning, match="Error shutting down b: boom"):
        registry.shutdown_all()

    assert "shutdown:c" in record
    assert "shutdown:a" in record
    assert record.index("shutdown:c") < record.index("shutdown:a")
    assert not any(registry.is_initialized(name) for name in ("a", "b", "c"))


def test_extension_error_is_isolated(registry):
    """ExtensionError remains isolated like any other Exception."""
    record = []
    registry.register(
        make_extension(
            "a", record=record, shutdown_error=ExtensionError("extension boom")
        )
    )
    registry.register(make_extension("b", record=record))
    registry.init_all(None)

    with pytest.warns(UserWarning, match="Error shutting down a: extension boom"):
        registry.shutdown_all()

    assert "shutdown:b" in record
    assert not registry.is_initialized("a")


def test_shutdown_does_not_catch_base_exception(registry):
    """BaseException (e.g. KeyboardInterrupt) must not be swallowed."""
    registry.register(
        make_extension("a", shutdown_error=KeyboardInterrupt("interrupted"))
    )
    registry.init_all(None)

    with pytest.raises(KeyboardInterrupt, match="interrupted"):
        registry.shutdown_all()
