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
        self.errors: List[Tuple[int, int, str]] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        """
        Visit assignment nodes and check if the assignment is to __all__.
        If so, check for:
          ANS100 - elements that are not strings
          ANS101 - duplicate entries
          ANS102 - empty __all__
          ANS103 - __all__ is not a list

        Args:
            node (ast.Assign): The assignment node to visit.
        """
        if hasattr(node.targets[0], 'id') and node.targets[0].id == '__all__':
            # ANS103: __all__ is not a list
            if not isinstance(node.value, ast.List):
                self.errors.append((
                    node.targets[0].lineno,
                    node.targets[0].col_offset,
                    "ANS103: '__all__' is not defined as a list.",
                ))
                self.generic_visit(node)
                return

            # ANS102: __all__ is empty
            if len(node.value.elts) == 0:
                self.errors.append((
                    node.targets[0].lineno,
                    node.targets[0].col_offset,
                    "ANS102: '__all__' is defined but empty.",
                ))

            seen: set = set()
            for element in node.value.elts:
                if isinstance(element, ast.Constant) and isinstance(
                    element.value, str
                ):
                    # ANS101: duplicate entry
                    if element.value in seen:
                        self.errors.append((
                            element.lineno,
                            element.col_offset,
                            "ANS101: '{0}' is a duplicate"
                            " entry in __all__.".format(element.value),
                        ))
                    else:
                        seen.add(element.value)
                else:
                    # ANS100: element is not a string
                    if isinstance(element, ast.Name):
                        label = element.id
                    elif isinstance(element, ast.Constant):
                        label = repr(element.value)
                    else:
                        label = type(element).__name__
                    self.errors.append((
                        element.lineno,
                        element.col_offset,
                        "ANS100: '{0}' import under __all__"
                        " is not a string.".format(label),
                    ))
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """
        Visit augmented assignment nodes (e.g. __all__ += [...]) and apply
        the same ANS100 check for non-string elements.

        Args:
            node (ast.AugAssign): The augmented assignment node to visit.
        """
        if (
            hasattr(node.target, 'id')
            and node.target.id == '__all__'
            and isinstance(node.value, ast.List)
        ):
            for element in node.value.elts:
                if not (
                    isinstance(element, ast.Constant)
                    and isinstance(element.value, str)
                ):
                    if isinstance(element, ast.Name):
                        label = element.id
                    elif isinstance(element, ast.Constant):
                        label = repr(element.value)
                    else:
                        label = type(element).__name__
                    self.errors.append((
                        element.lineno,
                        element.col_offset,
                        "ANS100: '{0}' import under __all__"
                        " is not a string.".format(label),
                    ))
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
        Run the plugin to find issues in __all__ assignments.

        Yields:
            Tuple[int, int, str, Type[Any]]: Line, column,
                                             error message
                                             and plugin type.
        """
        visitor = Visitor()
        visitor.visit(self._tree)
        for line, col, message in visitor.errors:
            yield line, col, message, type(self)
