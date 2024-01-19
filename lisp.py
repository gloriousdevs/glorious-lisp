"""
 source code --parsing--> syntax tree --interpret--> result

 [print 42]
 [print [+ 2 3]]

 [fn [x] [+ x 1]]

 [define name expr]

 [if test then else]

 [_fn_ args...]   # function call

 var              # variable reference

 [var]            # var()

 123

 [123 456 789]

"""

program = """
[define x 42]

[print [+ x 1]]
"""

fac = """
[define fac
  [fn [x]
    [if [<= x 0]
        1
        [* x [fac [- x 1]]]]]]
"""

from typing import Any
from dataclasses import dataclass
import re
import sys
import traceback

@dataclass
class Symbol:
    name: str


@dataclass
class Number:
    value: int


@dataclass
class Function:
    parameters: list[str]
    body: 'Value'


Value = Symbol | Number | list['Value'] | Function


def tokenize(text: str) -> list[str]:
    return re.findall(r'\[|\]|[^\[\]\s]+', text)


def parse_expression(tokens: list[str]) -> tuple[Value, list[str]] | None:
    if not tokens:
        return None

    if tokens[0] == '[':
        items = []
        tokens = tokens[1:]

        while tokens and tokens[0] != ']':
            result = parse_expression(tokens)
            if result is None:
                raise Exception("Expecting ], found end of program")
            value, tokens = result
            items.append(value)

        if not tokens:
            raise Exception("Expecting ], found end of program")

        return items, tokens[1:]

    if tokens[0] == ']':
        raise Exception("Unexpected ]")

    if tokens[0].isdigit():
        return Number(int(tokens[0])), tokens[1:]

    return Symbol(tokens[0]), tokens[1:]



def parse_program(tokens: list[str]) -> list[Value]:
    items = []

    while result := parse_expression(tokens):
        item, tokens = result
        items.append(item)

    return items


def evaluate(expression: Value, environment: dict[str, Value]) -> Value:
    match expression:
        case Number(_):
            return expression

        case Symbol(name):
            return environment[name]

        case []:
            return []

        case [Symbol("define"), Symbol(name), expression]:
            value = evaluate(expression, environment)
            environment[name] = value
            return value

        case [Symbol("if"), test, expression_if_true, expression_if_false]:
            test_value = evaluate(test, environment)
            if test_value:
                return evaluate(expression_if_true, environment)
            else:
                return evaluate(expression_if_false, environment)

        case [Symbol("fn"), parameters, body]:
            if not isinstance(parameters, list):
                raise Exception(f"Expected list of parameters, got {parameters} instead")

            parameter_names = []
            for parameter in parameters:
                if not isinstance(parameter, Symbol):
                    raise Exception(f"Expected parameter name, got {parameter} instead")
                parameter_names.append(parameter.name)

            function = Function(
                parameters=parameter_names,
                body=body,
            )
            return function

        case [head, *tail]:
            function = evaluate(head, environment)
            if callable(function):
                arguments = [evaluate(expression, environment) for expression in tail]
                return function(*arguments)
            else:
                raise Exception(f"{function} is not a function")

    raise Exception(f"Don't know how to evaluate {expression}")



standard_environment = {
    "+": lambda x, y: Number(x.value + y.value),
    "-": lambda x, y: Number(x.value - y.value),
    "*": lambda x, y: Number(x.value * y.value),
    "/": lambda x, y: Number(x.value / y.value),
    "<": lambda x, y: x.value < y.value,
    ">": lambda x, y: x.value > y.value,
    "print": print,
}

evaluate(parse_program(tokenize("[+ [* 3 4] [* 5 6]]"))[0], standard_environment)


def evaluate_file(filename: str, environment: dict[str, Value]) -> None:
    with open(filename) as program:
        expressions = parse_program(tokenize(program.read()))
        for expression in expressions:
            evaluate(expression, environment)

def repl(environment: dict[str, Value]) -> None:
    while True:
        try:
            program = input("lisp> ")
            expressions = parse_program(tokenize(program))
            for expression in expressions:
                result = evaluate(expression, environment)
                print(result)

        except EOFError:
            return

        except Exception as e:
            traceback.print_exc()



if __name__ == '__main__':
    match sys.argv:
        case [progname, filename]:
            evaluate_file(filename, standard_environment)

        case [progname]:
            repl(standard_environment)

        case [progname, *_]:
            print(f"Usage: {progname} [filename]")
