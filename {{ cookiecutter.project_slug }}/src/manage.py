import argparse
import asyncio

import sentry_sdk
from commands import *  # noqa: F401, F403
from commands.base import command_parser
from database import database


async def startup() -> None:
    await database.connect()


async def shutdown() -> None:
    await database.disconnect()


class ConsoleManager:
    @classmethod
    async def execute_command(cls, args: argparse.Namespace) -> None:
        if not hasattr(args, 'command') or args.command is None:
            raise ValueError('Command name is required')

        await args.command(args)


if __name__ == '__main__':
    args = command_parser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
    try:
        loop.run_until_complete(ConsoleManager.execute_command(args))
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(e)  # noqa: T201
    loop.run_until_complete(shutdown())
