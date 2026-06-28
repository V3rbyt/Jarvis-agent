"""Plugin helpers."""
from ..tools.base import Tool


def plugin(name, version="1.0.0", author="Unknown", description=""):
    def decorator(cls):
        cls.__plugin_name__ = name
        cls.__plugin_version__ = version
        cls.__plugin_author__ = author
        cls.__plugin_description__ = description
        return cls
    return decorator


def tool(name=None, description="", dangerous=False, requires_confirmation=False):
    def decorator(func):
        class FunctionTool(Tool): pass
        FunctionTool.name = name or func.__name__
        FunctionTool.description = description or (func.__doc__ or "")
        FunctionTool.dangerous = dangerous
        FunctionTool.requires_confirmation = requires_confirmation
        FunctionTool.execute = lambda self, params: func(params)
        return FunctionTool()
    return decorator
