import clang.cindex as cindex  # type: ignore
from .py_object import PyObject
from .py_field import PyField
from typing import TypeAlias

PyArgument: TypeAlias = PyField


class PyFunction(PyObject):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)
        self.arguments: list[PyArgument] = []
        self.returnType = cursor.result_type.spelling

        for child in cursor.get_children():
            if child.kind == cindex.CursorKind.PARM_DECL:
                self.arguments.append(PyArgument(child))
