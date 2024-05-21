import sys

import argparse
import asyncio
import logging

# idotmatrix imports
from cmd import CMD
from settings import settings
from youtube import youtube_subscribers

logger = logging.getLogger(__name__)


def get_parser(args):
    parser = argparse.ArgumentParser(
        description="control your 16x16 or 32x32 pixel displays"
    )
    # global argument
    parser.add_argument(
        "--address",
        action="store",
        help="the bluetooth address of the device",
    )

    parser.add_argument(
        "--channel",
        action="store",
        help="the channel id to view the subscribers",
    )
    # parse arguments
    return parser


async def main():

    log_format = (
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    logging.basicConfig(
        format=log_format,
    )

    cmd = CMD()

    parser = get_parser(sys.argv[1:])
    args = parser.parse_args()
    # cmd.add_arguments(parser)

    subscribers = await youtube_subscribers(settings.CHANNEL_ID, settings.API_KEY)

    logger.debug(f"El total de subs: {subscribers}")

    # run command
    # await cmd.run(args)


if __name__ == "__main__":
    log = logging.getLogger("idotmatrix")
    log.info("initialize app")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Caught keyboard interrupt. Stopping app.")
