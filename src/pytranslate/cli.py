import logging
import pathlib

import click

from pytranslate.asstranslator import ASSTranslator

logger = logging.getLogger(__name__)

AVAILABLE_LANGUAGES = ["DE", "EN", "FR", "ES", "IT", "NL", "PL"]
AVAILABLE_APIS = ["google", "deepl"]


@click.command()
@click.option("--log-level", help="Logging level", default="INFO", type=click.Choice(list(logging._nameToLevel.keys())))
@click.option("--log-format", help="Logging format", default="%(asctime)s | %(levelname)s | %(message)s", type=str)
@click.option("--log-dateformat", help="Logging date format", default="%Y-%m-%dT%H:%M:%S%z", type=str)
@click.option("--source", "-s", help="Source language", required=True, type=click.Choice(AVAILABLE_LANGUAGES))
@click.option("--destination", "-d", help="Destination language", required=True, type=click.Choice(AVAILABLE_LANGUAGES))
@click.option("--api", help="Translation API to use", required=True, type=click.Choice(AVAILABLE_APIS))
@click.option("--input", help="File to translate", required=True, type=str)
def cli(
    log_level: str,
    log_format: str,
    log_dateformat: str,
    source: str,
    destination: str,
    api: str,
    input: str,
) -> None:

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=log_dateformat,
    )

    file_extension = pathlib.Path(input).suffix
    if file_extension == ".ass":
        translator = ASSTranslator(file=input, tolang=destination, fromlang=source, api=api)
        translator.run()
    else:
        raise Exception("File type not supported")
