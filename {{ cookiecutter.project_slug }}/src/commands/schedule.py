from argparse import Namespace
from datetime import datetime
from typing import List
from typing import Optional
from typing import Type

from commands.base import BaseCommand
from commands.file_cleaner import FileCleaner
from croniter import croniter


class Job:
    def __init__(self, command: Type[BaseCommand], cron_pattern: Optional[str] = None) -> None:
        self.command = command
        self.cron_pattern = cron_pattern

    def every_hour(self) -> 'Job':
        self.cron_pattern = '0 * * * *'
        return self

    def every_day(self) -> 'Job':
        self.cron_pattern = '0 0 * * *'
        return self

    def every_minute(self) -> 'Job':
        self.cron_pattern = '* * * * *'
        return self

    def cron(self, cron_pattern: str) -> 'Job':
        self.cron_pattern = cron_pattern
        return self

    def is_due(self, now: datetime) -> bool:
        if self.cron_pattern is None:
            return False
        return croniter.match(self.cron_pattern, now)


class Scheduler:
    @classmethod
    def command(cls, command: Type[BaseCommand]) -> Job:
        return Job(command)


class Schedule(BaseCommand):
    command_name = 'schedule'
    help_text = 'Run scheduled commands.'
    schedule: Scheduler = Scheduler

    @classmethod
    async def get_jobs(cls) -> List[Job]:
        return [
            cls.schedule.command(FileCleaner).cron('0 0 * * *'),  # noqa: E800
        ]

    @classmethod
    async def run(cls, args: Optional[Namespace] = None) -> None:
        now = datetime.utcnow()
        for job in await cls.get_jobs():
            if job.is_due(now):
                await job.command.run()
