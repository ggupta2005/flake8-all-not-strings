import ast
from typing import Set

from flake8_all_not_strings import Plugin


def get_results(s: str) -> Set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree)
    return {"{}:{}: {}".format(*r) for r in plugin.run()}


# ---------------------------------------------------------------------------
# ANS101 - duplicate entries in __all__
# ---------------------------------------------------------------------------

class TestANS101:
    def test_no_duplicates(self):
        assert get_results('__all__ = ["foo", "bar"]') == set()

    def test_single_duplicate(self):
        results = get_results('__all__ = ["foo", "bar", "foo"]')
        assert any(
            "ANS101: 'foo' is a duplicate entry in __all__." in r
            for r in results
        )

    def test_multiple_duplicates(self):
        results = get_results('__all__ = ["a", "b", "a", "b"]')
        assert any("ANS101" in r and "'a'" in r for r in results)
        assert any("ANS101" in r and "'b'" in r for r in results)

    def test_duplicate_does_not_suppress_ans100(self):
        # Non-string plus a duplicate string: both ANS100 and ANS101 fire
        results = get_results('__all__ = [foo, "bar", "bar"]')
        assert any("ANS100" in r and "foo" in r for r in results)
        assert any("ANS101" in r and "bar" in r for r in results)

    def test_no_false_positive_single_entry(self):
        assert get_results('__all__ = ["foo"]') == set()

    def test_multiline_duplicate(self):
        code = '__all__ = [\n    "foo",\n    "bar",\n    "foo",\n]'
        results = get_results(code)
        assert any("ANS101" in r and "foo" in r for r in results)


# ---------------------------------------------------------------------------
# ANS102 - __all__ is defined but empty
# ---------------------------------------------------------------------------

class TestANS102:
    def test_empty_all(self):
        results = get_results("__all__ = []")
        assert any("ANS102" in r for r in results)

    def test_non_empty_all_no_error(self):
        assert get_results('__all__ = ["foo"]') == set()

    def test_empty_all_error_message(self):
        results = get_results("__all__ = []")
        assert any(
            "ANS102: '__all__' is defined but empty." in r for r in results
        )

    def test_empty_all_reports_correct_line(self):
        code = "x = 1\n__all__ = []"
        results = get_results(code)
        assert any(r.startswith("2:") and "ANS102" in r for r in results)


# ---------------------------------------------------------------------------
# ANS103 - __all__ is not a list
# ---------------------------------------------------------------------------

class TestANS103:
    def test_tuple_triggers_ans103(self):
        results = get_results('__all__ = ("foo", "bar")')
        assert any("ANS103" in r for r in results)

    def test_set_triggers_ans103(self):
        results = get_results('__all__ = {"foo", "bar"}')
        assert any("ANS103" in r for r in results)

    def test_list_no_ans103(self):
        results = get_results('__all__ = ["foo"]')
        assert not any("ANS103" in r for r in results)

    def test_ans103_error_message(self):
        results = get_results('__all__ = ("foo",)')
        assert any(
            "ANS103: '__all__' is not defined as a list." in r for r in results
        )

    def test_ans103_does_not_also_emit_ans100(self):
        # When ANS103 fires we return early — no ANS100/ANS102 should fire
        results = get_results('__all__ = ("foo", bar)')
        assert any("ANS103" in r for r in results)
        assert not any("ANS100" in r for r in results)
        assert not any("ANS102" in r for r in results)

    def test_ans103_reports_correct_line(self):
        code = "x = 1\n__all__ = ()"
        results = get_results(code)
        assert any(r.startswith("2:") and "ANS103" in r for r in results)
