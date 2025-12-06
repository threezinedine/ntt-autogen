import clang.cindex as cindex  # type: ignore
from .py_object import PyObject
from .py_enum_constant import PyEnumConstant


class PyEnum(PyObject):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)
        self.constants: list[PyEnumConstant] = []

        for child in cursor.get_children():
            if child.kind == cindex.CursorKind.ENUM_CONSTANT_DECL:
                self.constants.append(PyEnumConstant(child))
