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


@dataclass
class Symbol:
    name: str


@dataclass
class Number:
    value: int


Value = Symbol | Number | list['Value']


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

        case [head, *tail]:
            function = evaluate(head, environment)
            if callable(function):
                arguments = [evaluate(expression, environment) for expression in tail]
                return function(*arguments)

    raise Exception(f"Don't know how to evaluate {expression}")



standard_environment = {
    "+": lambda x, y: Number(x.value + y.value),
    "-": lambda x, y: Number(x.value - y.value),
    "*": lambda x, y: Number(x.value * y.value),
    "/": lambda x, y: Number(x.value / y.value),
}

evaluate(parse_program(tokenize("[+ [* 3 4] [* 5 6]]"))[0], standard_environment)
