from argparse import ArgumentParser, Namespace


def argument() -> Namespace:
    parser = ArgumentParser(
        prog="python3 -m src",
        description="project by vallangl"
    )
    parser.add_argument(
        "--input",
        default="data/input/function_calling_tests.json",
        type=str,
        help="prompts file"
    )
    parser.add_argument(
        "--output",
        default="data/output/function_calling_results.json",
        type=str,
        help="file with the answers"
    )
    parser.add_argument(
        "--functions_definition",
        default="data/input/functions_definition.json",
        type=str,
        help="file with the function definitions"
    )
    return parser.parse_args()
