import json
import sys
import argparse
from .parsing.arg import argument
from .loader import read_calling_tests, read_function_definition
from pydantic import ValidationError


def main():
    args = argument()
    functions = read_function_definition(args.functions_definition)
    test = read_calling_tests(args.input)
    print(test)
    print(functions)


if __name__ == "__main__":
    main()
