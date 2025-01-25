import json
import logging
import os

import click
from src.config.base_config import BaseConfig
from dotenv import load_dotenv

load_dotenv()

log_level = "INFO"
if log_level != "INFO":
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d"
else:
    log_format = "%(message)s"

logging.basicConfig(level=log_level, format=log_format)
logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    pass


@click.group()
def cli1() -> None:
    pass


@cli1.command("new")
def new_cli1() -> None:
    print("cli1 > new")


@click.group()
def cli2() -> None:
    pass


@cli2.command("new")
def new_cli2() -> None:
    print("cli2 > new")


if __name__ == "__main__":
    cli.add_command(cli1)
    cli.add_command(cli2)
    cli()
