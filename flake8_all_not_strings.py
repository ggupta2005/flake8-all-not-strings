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
        """Initialize the Visitor with an empty list to store errors."""
        self.errors: List[Tuple[int, int]] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        """
        Visit assignment nodes and check if the assignment is to __all__.
        If so, record any elements in __all__ that are not strings.

        Args:
            node (ast.List): The assignment node to visit.
        """
        if hasattr(node.targets[0], 'id') and node.targets[0].id == '__all__':
            for element in getattr(node.value, 'elts', []):
                if isinstance(element, ast.Name):
                    self.errors.append(
                        (element.lineno, element.col_offset, element.id)
                    )
                elif not isinstance(element, ast.Str) and not (hasattr(ast, 'Constant') and isinstance(element, ast.Constant) and isinstance(element.value, str)):
                    self.errors.append(
                        (element.lineno, element.col_offset, getattr(element, 'id', repr(element)))
                    )
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if hasattr(node.target, 'id') and node.target.id == '__all__':
            if isinstance(node.value, ast.List):
                for element in node.value.elts:
                    if isinstance(element, ast.Name):
                        self.errors.append(
                            (element.lineno, element.col_offset, element.id)
                        )
                    elif not isinstance(element, ast.Str) and not (hasattr(ast, 'Constant') and isinstance(element, ast.Constant) and isinstance(element.value, str)):
                        self.errors.append(
                            (element.lineno, element.col_offset, getattr(element, 'id', repr(element)))
                        )
        self.generic_visit(node)



class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree: ast.AST):
        """
        Initialize the Plugin with the AST tree to be checked.

        Args:
            tree (ast.AST): The abstract syntax tree of the file.
        """
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        """
        Run the plugin to find non-string elements in __all__ assignments.

        Yields:
            Tuple[int, int, str, Type[Any]]: Line, column,
                                             error message
                                             and plugin type.
        """
        visitor = Visitor()
        visitor.visit(self._tree)
        for line, col, element_name in visitor.errors:
            yield line, col, ("ANS100: '{0}' import under __all__"
                              " is not a string.").format(
                element_name), type(self)
