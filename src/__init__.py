"""
This module is the entry point for the package. It exports the `init` function"""
from src import langtrace
from src.utils.with_root_span import with_langtrace_root_span

__all__ = ['langtrace', 'with_langtrace_root_span']
