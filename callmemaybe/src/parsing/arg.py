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
        help="fichier de prompts"
    )
    parser.add_argument(
        "--output",
        default="data/output/function_calling_result.json",
        type=str,
        help="fichier avec les reponses"
    )
    parser.add_argument(
        "--functions_definition",
        default="data/input/functions_definition.json",
        type=str,
        help="fichier avec les def des fonctions"
    )
    return parser.parse_args()
