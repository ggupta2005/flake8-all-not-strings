import ast
from typing import Set

from flake8_all_not_strings import Plugin


def get_results(s: str) -> Set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree)
    return {'{}:{}: {}'.format(*r) for r in plugin.run()}


class TestFlake8AllNotStrings:
    def test_flake8_all_not_strings(self):
        assert get_results("") == set()
        assert get_results("__all__ = [\nsomething,\nsomething_else]") == set(
            [
                '3:0: ANS100: Some imports under all are not strings.',
                '2:0: ANS100: Some imports under all are not strings.'
            ]
        )
