import pytest  # type: ignore
from ntt_autogen.analyze import Parser


def test_parse_simple_typedef():
    code = """
typedef int MyInt;
"""

    parser = Parser(code)
    parser.Parse()

    assert len(parser.Typedefs) == 1
    typedef = parser.Typedefs[0]
    assert typedef.name == "MyInt"
    assert typedef.annotations == []
    assert typedef.underlyingType == "int"


def test_parse_typedef_with_annotations():
    code = """
typedef __attribute__((annotate("custom_type"))) float MyFloat;
"""

    parser = Parser(code)
    parser.Parse()
    assert len(parser.Typedefs) == 1
    typedef = parser.Typedefs[0]
    assert typedef.name == "MyFloat"
    assert typedef.annotations == ["custom_type"]
    assert typedef.underlyingType == "float"


def test_parse_function_pointer_typedef():
    code = """
typedef void (*Callback)(int);
"""

    parser = Parser(code)
    parser.Parse()
    assert len(parser.Typedefs) == 1

    typedef = parser.Typedefs[0]
    assert typedef.name == "Callback"
    assert typedef.annotations == []
    assert typedef.underlyingType == "void (*)(int)"


def test_parse_typedef_struct():
    code = """
typedef struct {
    int x;
    int y;
} Point;
"""

    parser = Parser(code)
    parser.Parse()
    assert len(parser.Typedefs) == 1
    typedef = parser.Typedefs[0]
    assert typedef.name == "Point"
    assert typedef.annotations == []
    assert typedef.underlyingType == "struct Point"

    assert len(parser.Structs) == 1
    struct = parser.Structs[0]
    assert struct.name == "Point"
    assert len(struct.fields) == 2
    assert struct.fields[0].name == "x"
    assert struct.fields[0].type == "int"
    assert struct.fields[1].name == "y"
    assert struct.fields[1].type == "int"


def test_parse_typedef_with_comment():
    code = """
/** This is a typedef for MyChar */
typedef char MyChar;
"""

    parser = Parser(code)
    parser.Parse()
    assert len(parser.Typedefs) == 1
    typedef = parser.Typedefs[0]
    assert typedef.name == "MyChar"
    assert typedef.annotations == []
    assert typedef.underlyingType == "char"
    assert typedef.comment == "This is a typedef for MyChar"


def test_parse_function_pointer_typedef_with_comment():
    code = """
/**
 * @brief Typedef for a callback function that takes an integer argument and returns void.
 * @param int The integer argument.
 * @return void
 */
typedef void (*Callback)(int);
"""

    parser = Parser(code)
    parser.Parse()
    assert len(parser.Typedefs) == 1
    typedef = parser.Typedefs[0]
    assert typedef.name == "Callback"
    assert typedef.annotations == []
    assert typedef.underlyingType == "void (*)(int)"
    assert (
        typedef.comment
        == "Typedef for a callback function that takes an integer argument and returns void."
    )
