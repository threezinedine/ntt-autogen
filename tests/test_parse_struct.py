import pytest  # type: ignore
from ntt_autogen.analyze import Parser


def test_parse_simple_struct():
    code = """
struct Simple {
    int a;
    float b;
};
"""
    parser = Parser(code)
    parser.Parse()
    assert len(parser.Structs) == 1

    struct = parser.Structs[0]
    assert struct.name == "Simple"
    assert len(struct.fields) == 2

    assert struct.fields[0].name == "a"
    assert struct.fields[0].type == "int"

    assert struct.fields[1].name == "b"
    assert struct.fields[1].type == "float"


def test_parse_struct_with_annotations():
    code = """
struct __attribute__((annotate("binding"))) Annotated {
    int x __attribute__((annotate("primary")));
    double y __attribute__((annotate("secondary")));
};
"""

    parser = Parser(code)
    parser.Parse()

    assert len(parser.Structs) == 1
    struct = parser.Structs[0]
    assert struct.name == "Annotated"
    assert struct.annotations == ["binding"]

    assert len(struct.fields) == 2
    assert struct.fields[0].name == "x"
    assert struct.fields[0].type == "int"
    assert struct.fields[0].annotations == ["primary"]

    assert struct.fields[1].name == "y"
    assert struct.fields[1].type == "double"
    assert struct.fields[1].annotations == ["secondary"]


def test_parse_empty_struct():
    code = """
struct Empty {
};
"""
    parser = Parser(code)
    parser.Parse()
    assert len(parser.Structs) == 1

    struct = parser.Structs[0]
    assert struct.name == "Empty"
    assert len(struct.fields) == 0


def test_parse_struct_with_multiple_annotations():
    code = """
struct __attribute__((annotate("first"))) __attribute__((annotate("second"))) WithDefaults {
    int a;
    float b;
};
"""

    parser = Parser(code)
    parser.Parse()

    assert len(parser.Structs) == 1
    struct = parser.Structs[0]
    assert struct.name == "WithDefaults"
    assert len(struct.fields) == 2
    assert struct.annotations == ["first", "second"]


def test_parse_struct_field_comment():
    code = """
/**
 * @brief This is a struct with comments on its fields.
 */
struct WithComments {
    int a; ///< This is field a
    /** This is field b */
    float b;
};
"""

    parser = Parser(code)
    parser.Parse()

    assert len(parser.Structs) == 1
    struct = parser.Structs[0]
    assert struct.name == "WithComments"
    assert struct.comment == "This is a struct with comments on its fields."
    assert len(struct.fields) == 2

    assert struct.fields[0].name == "a"
    assert struct.fields[0].type == "int"
    assert struct.fields[0].comment == "This is field a"

    assert struct.fields[1].name == "b"
    assert struct.fields[1].type == "float"
    assert struct.fields[1].comment == "This is field b"
