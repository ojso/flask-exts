import pytest
from flask import Flask
from markupsafe import Markup

from flask_exts.frontend.plugin_manager import PluginCycleError, PluginManager


class FakePlugin:
    def __init__(self, name, dependencies=(), style="", script=""):
        self.name = name
        self.dependencies = list(dependencies)
        self._style = style
        self._script = script

    def style(self):
        return self._style

    def script(self):
        return self._script


@pytest.fixture
def manager():
    return PluginManager()


@pytest.fixture
def app():
    return Flask(__name__)


def test_register_plugin_rejects_duplicate_names(manager):
    manager.register_plugin(FakePlugin("a"))

    with pytest.raises(ValueError, match="already registered"):
        manager.register_plugin(FakePlugin("a"))


def test_set_default_plugins_keeps_registered_names_in_input_order(manager):
    manager.register_plugin(FakePlugin("a"))
    manager.register_plugin(FakePlugin("b"))

    manager.set_default_plugins(["a", "missing", "b", "c"])

    assert manager._default_plugins == ["a", "b"]


def test_request_plugins_are_ordered_after_dependencies(manager, app):
    manager.register_plugin(FakePlugin("a"))
    manager.register_plugin(FakePlugin("b", dependencies=["a"]))
    manager.register_plugin(FakePlugin("c"))

    with app.test_request_context():
        manager.set_default_plugins(["a"])
        manager.add_request_plugins(["c"])

        assert manager.get_request_plugins() == ["c"]
        assert manager.ordered_names() == ["a", "c"]

        manager.add_request_plugins(["b"])

        assert manager.get_request_plugins() == ["c", "b"]
        assert manager.ordered_names() == ["a", "c", "b"]


def test_ordered_names_detects_circular_dependencies(manager, app):
    manager.register_plugin(FakePlugin("first", dependencies=["second"]))
    manager.register_plugin(FakePlugin("second", dependencies=["first"]))

    with app.test_request_context():
        manager.add_request_plugins(["first"])

        with pytest.raises(
            PluginCycleError,
            match="Circular plugin dependency: first -> second -> first",
        ):
            manager.ordered_names()


def test_load_resources_returns_markup_in_dependency_order(manager, app):
    manager.register_plugin(FakePlugin("base", style="base-css", script="base-js"))
    manager.register_plugin(
        FakePlugin(
            "feature",
            dependencies=["base"],
            style="feature-css",
            script="feature-js",
        )
    )

    with app.test_request_context():
        manager.add_request_plugins(["feature"])

        assert manager.load_styles() == Markup("base-css\nfeature-css")
        assert manager.load_scripts() == Markup("base-js\nfeature-js")
