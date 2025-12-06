import clang.cindex as cindex  # type: ignore


class PyObject:
    def __init__(self, cursor: cindex.Cursor):
        self.name: str = cursor.spelling
        self.annotations: list[str] = []
        self.comment: str | None = cursor.brief_comment or None
        self.rawComent: str | None = cursor.raw_comment or None

        for cursor in cursor.get_children():
            if cursor.kind == cindex.CursorKind.ANNOTATE_ATTR:
                self.annotations.append(cursor.displayname)
