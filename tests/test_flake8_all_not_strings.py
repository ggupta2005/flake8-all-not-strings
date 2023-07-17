import ast
from typing import Set
import subprocess

from flake8_all_not_strings import Plugin


def get_results(s: str) -> Set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree)
    return {'{}:{}: {}'.format(*r) for r in plugin.run()}


class TestFlake8AllNotStrings:
    def test_flake8_all_not_strings_in_flake8_command(self):
        command = "flake8 --version"
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "flake8-all-not-strings" in result.stdout

    def test_flake8_all_not_strings(self):
        assert get_results("") == set()
        assert get_results("__all__ = [\nsomething,\nsomething_else]") == set(
            [
                '3:0: ANS100: Some imports under all are not strings.',
                '2:0: ANS100: Some imports under all are not strings.'
            ]
        )
