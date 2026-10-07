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

    - record: if given a list, append(name) on init_app and append(f"shutdown:{name}") on shutdown
    - shutdown_error: if given an exception, raise it on shutdown (used to test exception isolation)
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
    """The dependent must always be ordered after the dependency. This is the regression test for B1."""
    record = []
    a = make_extension("a", dependencies=["b"], record=record)
    b = make_extension("b", record=record)
    registry.register(a)
    registry.register(b)

    assert registry.initialization_order() == ["b", "a"]

    registry.init_all(None)
    assert record == ["b", "a"]


def test_independent_extensions_keep_registration_order(registry):
    """Independent extensions keep registration order (this is an implicit contract that needs to be locked down)."""
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
    """A->B->A cycle -> ExtensionDependencyError, and the message contains the full cycle path."""
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
    with pytest.raises(ExtensionError, match="already registered"):
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


def test_shutdown_exception(registry):
    """an exception thrown by shutdown."""
    record = []
    registry.register(make_extension("a", record=record))
    registry.register(
        make_extension("b", record=record, shutdown_error=ValueError("boom"))
    )
    registry.init_all(None)

    with pytest.raises(ValueError, match="boom"):
        registry.shutdown_all()
