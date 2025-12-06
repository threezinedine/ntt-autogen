import pytest  # type: ignore
from ntt_autogen.analyze import Parser


def test_parse_simple_enum():
    code = """
enum Simple {
    SIMPLE_A,
    SIMPLE_B,
};
"""
    parser = Parser(code)
    parser.Parse()
    assert len(parser.Enums) == 1

    enum = parser.Enums[0]
    assert enum.name == "Simple"
    assert len(enum.constants) == 2

    assert enum.constants[0].name == "SIMPLE_A"
    assert enum.constants[0].value == 0
    assert enum.constants[0].annotations == []
    assert enum.constants[1].name == "SIMPLE_B"
    assert enum.constants[1].value == 1
    assert enum.constants[1].annotations == []


def test_parse_enum_with_annotations():
    code = """
enum __attribute__((annotate("color_enum"))) Color {
    RED __attribute__((annotate("primary"))),
    GREEN __attribute__((annotate("secondary"))),
    BLUE __attribute__((annotate("primary"))),
};
"""
    parser = Parser(code)
    parser.Parse()

    assert len(parser.Enums) == 1
    enum = parser.Enums[0]
    assert enum.name == "Color"
    assert enum.annotations == ["color_enum"]
    assert len(enum.constants) == 3
    assert enum.constants[0].name == "RED"
    assert enum.constants[0].value == 0
    assert enum.constants[0].annotations == ["primary"]
    assert enum.constants[1].name == "GREEN"
    assert enum.constants[1].value == 1
    assert enum.constants[1].annotations == ["secondary"]
    assert enum.constants[2].name == "BLUE"
    assert enum.constants[2].value == 2
    assert enum.constants[2].annotations == ["primary"]


def test_parse_enum_with_explicit_values():
    code = """
enum Numbers {
    ONE = 1,
    TWO = 2,
    TEN = 10,
};
"""

    parser = Parser(code)
    parser.Parse()
    assert len(parser.Enums) == 1
    enum = parser.Enums[0]
    assert enum.name == "Numbers"
    assert len(enum.constants) == 3
    assert enum.constants[0].name == "ONE"
    assert enum.constants[0].value == 1
    assert enum.constants[1].name == "TWO"
    assert enum.constants[1].value == 2
    assert enum.constants[2].name == "TEN"
    assert enum.constants[2].value == 10


def test_parse_enum_with_comments():
    code = """
/**
 * @brief Status enumeration
 */
enum Status {
    SUCCESS, ///< Success status
    WARNING,
    /** Error status */
    ERROR,
};
"""

    parser = Parser(code)
    parser.Parse()
    assert len(parser.Enums) == 1
    enum = parser.Enums[0]
    assert enum.name == "Status"
    assert enum.comment == "Status enumeration"
    assert len(enum.constants) == 3

    assert enum.constants[0].name == "SUCCESS"
    assert enum.constants[0].value == 0
    assert enum.constants[0].comment == "Success status"

    assert enum.constants[1].name == "WARNING"
    assert enum.constants[1].value == 1
    assert enum.constants[1].comment == None

    assert enum.constants[2].name == "ERROR"
    assert enum.constants[2].value == 2
    assert enum.constants[2].comment == "Error status"
