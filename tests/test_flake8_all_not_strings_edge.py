import ast
from flake8_all_not_strings import Plugin

def get_results(s: str):
    tree = ast.parse(s)
    plugin = Plugin(tree)
    return sorted(['{}:{}: {}'.format(*r) for r in plugin.run()])


def test_nested_lists_in_all():
    code = """
__all__ = ["foo", ["bar", "baz"], 123]
"""
    results = get_results(code)
    assert any("is not a string" in r for r in results)

def test_augmented_assignment():
    code = """
__all__ = ["foo"]
__all__ += [bar]
"""
    results = get_results(code)
    assert any("bar" in r for r in results)

def test_conditional_all():
    code = """
if True:
    __all__ = [foo]
else:
    __all__ = ["bar"]
"""
    results = get_results(code)
    assert any("foo" in r for r in results)

def test_multiline_all():
    code = """
__all__ = [
    "foo",
    bar,
    "baz",
]
"""
    results = get_results(code)
    assert any("bar" in r for r in results)

def test_all_with_comments_and_whitespace():
    code = """
__all__ = [  # exports
    "foo",  # ok
    bar,     # not ok
]
"""
    results = get_results(code)
    assert any("bar" in r for r in results)
