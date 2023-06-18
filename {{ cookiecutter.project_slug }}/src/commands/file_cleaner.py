import argparse
import os
import time
from typing import Optional

from commands.base import BaseCommand

from api.v1.files.repositories import FileRepository


class FileCleaner(BaseCommand):
    command_name = 'file-cleaner'
    help_text = 'Clean files from tmp directory.'

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '-d',
            '--days',
            type=str,
            help='Number of days to keep files in tmp directory.',
            default=7,
        )

    @classmethod
    async def run(cls, args: Optional[argparse.Namespace] = None) -> None:
        now = time.time()
        days = now - (args.days * 86400)
        for file in os.listdir(FileRepository.tmp_path):
            file_path = os.path.join(FileRepository.tmp_path, file)
            if os.path.isfile(file_path) and not file.startswith('.') and os.stat(file_path).st_mtime < days:
                os.remove(file_path)
