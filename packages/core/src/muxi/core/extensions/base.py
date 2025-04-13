"""
Base Extension Module

This module defines the base Extension class that all MUXI extensions must inherit from.
Extensions are registered in a central registry and can be loaded by name.
"""


class Extension:
    """Base class for all MUXI extensions.

    Extensions provide additional functionality to the MUXI framework and
    can be loaded either declaratively or programmatically.
    """
    name = None
    _registry = {}

    @classmethod
    def register(cls, extension_cls):
        """Register an extension class in the global registry.

        Args:
            extension_cls: The extension class to register

        Returns:
            The registered extension class (for decorator usage)
        """
        if not extension_cls.name:
            raise ValueError("Extension must define a 'name' class attribute")
        cls._registry[extension_cls.name] = extension_cls
        return extension_cls

    @classmethod
    def get(cls, name):
        """Get an extension class by name.

        Args:
            name: The name of the extension

        Returns:
            The extension class, or None if not found
        """
        return cls._registry.get(name)

    @classmethod
    def list(cls):
        """List all registered extensions.

        Returns:
            A list of registered extension names
        """
        return list(cls._registry.keys())

    @classmethod
    def init(cls, **kwargs):
        """Initialize the extension.

        This method must be implemented by each extension.

        Args:
            **kwargs: Extension-specific initialization parameters

        Raises:
            NotImplementedError: If the extension does not implement this method
        """
        raise NotImplementedError(
            f"Extension {cls.__name__} does not implement the init method"
        )
