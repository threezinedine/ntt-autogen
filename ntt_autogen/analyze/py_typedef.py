import clang.cindex as cindex  # type: ignore
from .py_object import PyObject


class PyTypedef(PyObject):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)
        self.underlyingType = cursor.underlying_typedef_type.spelling

    def __repr__(self) -> str:
        return f'<PyTypedef name="{self.name}" underlyingType="{self.underlyingType}">'
