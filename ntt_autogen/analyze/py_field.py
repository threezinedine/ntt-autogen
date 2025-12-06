import clang.cindex as cindex  # type: ignore
from .py_object import PyObject


class PyField(PyObject):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)
        self.type = cursor.type.spelling
