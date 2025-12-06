import pytest  # type: ignore
from ntt_autogen.analyze import Parser


def test_parse_simple_function():
    code = """
void simpleFunction(int a, float b);
"""

    parser = Parser(code)
    parser.Parse()

    assert len(parser.Functions) == 1
    function = parser.Functions[0]
    assert function.name == "simpleFunction"
    assert function.returnType == "void"

    assert len(function.arguments) == 2
    assert function.arguments[0].name == "a"
    assert function.arguments[0].type == "int"
    assert function.arguments[1].name == "b"
    assert function.arguments[1].type == "float"


def test_parse_function_no_arguments():
    code = """
int noArgFunction();
"""

    parser = Parser(code)
    parser.Parse()

    assert len(parser.Functions) == 1
    function = parser.Functions[0]
    assert function.name == "noArgFunction"
    assert function.returnType == "int"
    assert len(function.arguments) == 0


def test_parse_function_pointer_argument():
    code = """
void callbackFunction(void (*callback)(int));
"""

    parser = Parser(code)
    parser.Parse()

    assert len(parser.Functions) == 1
    function = parser.Functions[0]
    assert function.name == "callbackFunction"
    assert function.returnType == "void"

    assert len(function.arguments) == 1
    assert function.arguments[0].name == "callback"
    assert function.arguments[0].type == "void (*)(int)"


def test_parse_function_with_annotations():
    code = """
int __attribute__((annotate("exported")))  annotatedFunction(int x __attribute__((annotate("input"))));
"""

    parser = Parser(code)
    parser.Parse()

    assert len(parser.Functions) == 1
    function = parser.Functions[0]
    assert function.name == "annotatedFunction"
    assert function.returnType == "int"
    assert function.annotations == ["exported"]

    assert len(function.arguments) == 1
    assert function.arguments[0].name == "x"
    assert function.arguments[0].type == "int"
    assert function.arguments[0].annotations == ["input"]


def test_parse_function_with_comment():
    code = """
/**
 * @brief This is a sample function.
 * @param x An integer parameter.
 * @return An integer result.
 */
int documentedFunction(int x);
"""

    parser = Parser(code)
    parser.Parse()

    assert len(parser.Functions) == 1
    function = parser.Functions[0]
    assert function.name == "documentedFunction"
    assert function.returnType == "int"
    assert function.comment == "This is a sample function."

    assert len(function.arguments) == 1
    assert function.arguments[0].name == "x"
    assert function.arguments[0].type == "int"
