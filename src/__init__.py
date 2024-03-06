"""
This module is the entry point for the package. It exports the `init` function"""
from src.init import init
from src.utils.with_root_span import with_langtrace_root_span

__all__ = ['init', 'with_langtrace_root_span']
