import json
import sys
import argparse

from src import arg

from pydantic import ValidationError


def main():
    args=argument()
    # ecrire le fichier
    try:
        with open("data/input/function_calling_tests.json") as f:
            data = json.load(f)
        print(data)
    except ValidationError as err:
        print(err)


if __name__ == "__main__":
    main()
