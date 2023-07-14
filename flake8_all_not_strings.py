import ast
import sys
from typing import Any, Generator, List, Tuple, Type

if sys.version_info < (3, 8):  # pragma: no cover (<PY38)
    # Third party
    import importlib_metadata
else:  # pragma: no cover (PY38+)
    # Core Library
    import importlib.metadata as importlib_metadata


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: List[Tuple[int, int]] = []

    def visit_Assign(self, node: ast.List) -> None:
        # import pdb
        # pdb.set_trace()
        if hasattr(node.targets[0], 'id') and node.targets[0].id == '__all__':
            for element in node.value.elts:
                # import pdb
                # pdb.set_trace()
                if isinstance(element, ast.Name):
                    self.errors.append((element.lineno, element.col_offset))
        self.generic_visit(node)


class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree: ast.AST):
        # import pdb
        # pdb.set_trace()
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)
        for line, col in visitor.errors:
            yield line, col, "ANS100: Some imports under all are not strings.", type(self)

