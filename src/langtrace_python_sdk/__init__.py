"""
This module is the entry point for the package. It exports the `init` function"""
from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

__all__ = ['langtrace', 'with_langtrace_root_span']
