from __future__ import annotations

import inspect
from datetime import timedelta

from src.types import clock as clock_module
from src.types.clock import TestClock


def test_E1S1_advance_moves_time_forward_with_no_sleep() -> None:
    c = TestClock()
    start = c.now()
    c.advance(15)
    assert c.now() == start + timedelta(minutes=15)


def test_E1S1_clock_module_has_no_float_literal() -> None:
    import ast

    source = inspect.getsource(clock_module)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "float":
            raise AssertionError("float type used in Clock module")
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            raise AssertionError("float literal used in Clock module")
