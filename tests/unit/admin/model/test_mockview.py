import pytest

from .mock_backend import MockBackend
from .mock_model import MockModel
from .mock_modelview import MockModelView


@pytest.fixture
def view():
    """Create a MockModelView."""
    initial_data = [
        {"id": 1, "col1": "col1_1", "col2": "col2_1", "col3": "col3_1"},
        {"id": 2, "col1": "col1_2", "col2": "col2_2", "col3": "col3_2"},
        {"id": 3, "col1": "col1_3", "col2": "col2_3", "col3": "col3_3"},
        {"id": 4, "col1": "col1_4", "col2": "col2_4", "col3": "col3_4"},
        {"id": 5, "col1": "col1_5", "col2": "col2_5", "col3": "col3_5"},
    ]

    def backend_factory(model, view, **kwargs):
        return MockBackend(model=model, view=view, data=initial_data)

    view = MockModelView(
        MockModel,
        backend_factory,
        name="test",
        endpoint="test",
        can_export=True,
        column_list=["col1", "col2"],
        column_labels={"col1": "Column 1", "col2": "Column 2"},
    )

    view.n_initial = len(initial_data)

    return view


# =============================================================================
# Column Configuration Tests
# =============================================================================


def test_mockview_column_list(view):
    """Test column list configuration."""
    columns = view.get_list_columns()
    assert columns == [("col1", "Column 1"), ("col2", "Column 2")]


def test_mockview_sortable_columns(view):
    """Test sortable columns."""
    sortable = view.get_sortable_columns()
    assert "col1" in sortable
    assert "col2" not in sortable


def test_mockview_column_labels(view):
    """Test column labels."""
    assert view.get_column_label("col1") == "Column 1"
    assert view.get_column_label("col2") == "Column 2"
    assert view.get_column_label("col3") == "Col3"


# =============================================================================
# CRUD Operations Tests
# =============================================================================


def test_mockview_create(view):
    data = view.get_data()
    model = view.model(col1="new_col1", col2="new_col2", col3="new_col3")
    view.create_model(model)
    assert len(data) == view.n_initial + 1
    last = data[-1]
    assert last.id == view.n_initial + 1
    assert last.col1 == "new_col1"
    assert last.col2 == "new_col2"
    assert last.col3 == "new_col3"


def test_mockview_update(view):
    model = view.get_one(1)
    model.col1 = "updated_col1"
    model.col2 = "updated_col2"
    view.update_model(model)
    model = view.get_one(1)
    assert model.col1 == "updated_col1"
    assert model.col2 == "updated_col2"


def test_mockview_delete(view):
    model = view.get_one(1)
    assert model is not None
    view.delete_model(model)
    model = view.get_one(1)
    assert model is None


# =============================================================================
# Delete Multiple Tests
# =============================================================================


def test_mockview_delete_multiple(view):
    """Test deleting multiple models."""
    view.delete_model_by_pk_ids([1, 2])
    data = view.get_data()
    assert len(data) == view.n_initial - 2
    assert data[0].id == 3


# =============================================================================
# Get One Test
# =============================================================================


def test_mockview_get_one(view):
    """Test getting a single model."""
    model = view.get_one(1)
    assert model.id == 1
    assert model.col1 == "col1_1"
    assert model.col2 == "col2_1"
    assert model.col3 == "col3_1"


# =============================================================================
# List Test
# =============================================================================


def test_mockview_get_list(view):
    """Test getting a list of models."""
    data = view.get_data()
    n_data = len(data)
    result = view.get_list()
    assert result["total"] == n_data
    assert result["count"] == n_data
    assert len(result["items"]) == n_data

    result = view.get_list(page=1, page_size=10)
    assert result["total"] == n_data
    assert result["count"] == n_data
    assert len(result["items"]) == n_data


# =============================================================================
# Pagination Tests
# =============================================================================


def test_mockview_get_list_with_pagination(view):
    result = view.get_list(
        page=1,
        page_size=2,
    )
    assert result["total"] == view.n_initial
    assert result["page"] == 1
    assert len(result["items"]) == 2
    assert result["page_size"] == 2
    assert result["page_count"] == 3

    result = view.get_list(
        page=2,
        page_size=2,
    )
    assert result["page"] == 2
    assert len(result["items"]) == 2

    result = view.get_list(
        page=3,
        page_size=2,
    )
    assert result["page"] == 3
    assert len(result["items"]) == 1


# =============================================================================
# Search Tests
# =============================================================================


def test_mockview_get_list_with_search(view):
    result = view.get_list(
        search="col1_2",
        page=1,
        page_size=10,
    )
    assert result["total"] == 1
    assert len(result["items"]) == 1


# =============================================================================
# Filter Tests
# =============================================================================


def test_mockview_get_list_with_filters(view):
    result = view.get_list(
        filters=[("col1", "eq", "col1_2")],
        page=1,
        page_size=10,
    )
    assert result["total"] == 1
    assert len(result["items"]) == 1


# =============================================================================
# Sorting Tests
# =============================================================================


def test_mockview_get_list_with_sorting(view):
    """Test ascending sorting."""
    result = view.get_list(
        sort_field="col1",
        sort_desc=False,
        page=1,
        page_size=10,
    )
    assert result["total"] == view.n_initial
    assert len(result["items"]) == view.n_initial
    assert result["items"][0]["col1"] == "col1_1"

    # Test descending sorting
    result = view.get_list(
        sort_field="col1",
        sort_desc=True,
        page=1,
        page_size=10,
    )
    assert result["total"] == view.n_initial
    assert len(result["items"]) == view.n_initial
    assert result["items"][0]["col1"] == "col1_5"
