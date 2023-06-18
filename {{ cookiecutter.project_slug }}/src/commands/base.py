import abc
from argparse import ArgumentParser
from argparse import Namespace
from typing import Optional

from config import settings

command_parser = ArgumentParser()
command_parser.add_argument(
    '-v',
    '--version',
    action='version',
    version=f'{settings.PROJECT_NAME} v{settings.RELEASE}',
    help='Show version',
)
subparsers = command_parser.add_subparsers()


class BaseCommand:
    command_name: str

    @classmethod
    @abc.abstractmethod
    async def run(cls, args: Optional[Namespace] = None) -> None:
        pass

    @classmethod
    def create_parser(cls) -> None:
        parser = subparsers.add_parser(cls.command_name, help=cls.help_text if hasattr(cls, 'help_text') else None)
        cls.add_arguments(parser)
        parser.set_defaults(command=cls.run)

    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        pass

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.create_parser()
