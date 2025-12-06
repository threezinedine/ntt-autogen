import clang.cindex as cindex  # type: ignore
from .py_field import PyField
from .py_object import PyObject


class PyStruct(PyObject):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)
        self.fields: list[PyField] = []

        for child in cursor.get_children():
            if child.kind == cindex.CursorKind.FIELD_DECL:
                self.fields.append(PyField(child))

    def __repr__(self) -> str:
        return f'<PyStruct name="{self.name}" />'
