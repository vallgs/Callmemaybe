import json
import sys
import argparse

from src import arg
from loader import read_calling_tests, read_function_definition
from pydantic import ValidationError


def main():
    tests = read_calling_tests()
    functions = read_function_definition()

    for test in tests:
        print(f"Test à exécuter : {test.prompt}")

if __name__ == "__main__":
    main()
