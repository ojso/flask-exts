class DynamicMockModel:
    """Dynamic mock model for testing with support for multiple data types.

    Features:
    - Dynamic attribute addition/deletion
    - Initialization from dict or class dict
    - Support for various data types: numbers, strings, dates, lists, dicts, etc.
    - Backward compatible with existing tests

    Example usage:
        # Basic usage with keyword args
        model = DynamicMockModel(id=1, col1="text", col2=42)

        # From dict (unpacked)
        data = {"id": 1, "col1": "text", "col2": 42, "col3": ["a", "b", "c"]}
        model = DynamicMockModel(**data)

        # Dynamic attribute
        model.dynamic_attr = "dynamic value"
    """

    def __init__(self, id=None, **kwargs):
        """Initialize DynamicMockModel.

        Args:
            id: Primary key value
            **kwargs: Any attributes to set on the model
        """
        self.id = id
        # Set all kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data_dict):
        """Create instance from a dictionary.

        Args:
            data_dict: Dictionary with attribute names as keys

        Returns:
            DynamicMockModel instance
        """
        return cls(**data_dict)

    def __repr__(self):
        """String representation."""
        attrs = [f"{k}={v!r}" for k, v in sorted(self.__dict__.items())]
        return f"DynamicMockModel({', '.join(attrs)})"

    def to_dict(self):
        """Convert model to dictionary.

        Returns:
            Dictionary with all model attributes
        """
        return {k: v for k, v in self.__dict__.items()}

    def set_attr(self, name, value):
        """Dynamically set an attribute.

        Args:
            name: Attribute name
            value: Attribute value
        """
        setattr(self, name, value)

    def del_attr(self, name):
        """Dynamically delete an attribute.

        Args:
            name: Attribute name to delete
        """
        if hasattr(self, name):
            delattr(self, name)

    def has_attr(self, name):
        """Check if attribute exists.

        Args:
            name: Attribute name

        Returns:
            True if attribute exists, False otherwise
        """
        return hasattr(self, name)

    def get_attr(self, name, default=None):
        """Get attribute value safely.

        Args:
            name: Attribute name
            default: Default value if attribute doesn't exist

        Returns:
            Attribute value or default
        """
        return getattr(self, name, default)
