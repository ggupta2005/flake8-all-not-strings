# flake8-all-not-strings
Flake8 plugin that checks that the all the elements defined in the `__all__` list are strings. Sometimes the flake8 doesn't throw error from the `__init__.py` if the modules under `__all__` are not strings.

Example below of an `__init__.py` file which should throw an error:-
```
from some_module import some_function 
__all__ = [
      some_function
]
```

Example below of an `__init__.py` file which should not throw an error:-
```
from some_module import some_function 
__all__ = [
      'some_function'
]
```

## Installation
```
pip install flake8-all-not-strings
```

## Flake8 codes
| Code | description |
|----------|----------|
| ANS100 | '<<some_module_name>>' import under __all__ is not a string. |
