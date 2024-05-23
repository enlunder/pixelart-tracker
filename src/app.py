import sys
import tempfile
import time
from pathlib import Path

import argparse
import asyncio
import logging

# idotmatrix imports
from screen import IDotMatrixScreen

from settings import settings
from youtube import youtube_subscribers, format_subscribers, create_subscribers_image

logger = logging.getLogger(__name__)


def parse_arguments(args):
    parser = argparse.ArgumentParser(
        description="control your 16x16 or 32x32 pixel displays"
    )
    parser.add_argument(
        "--address",
        action="store",
        help="the bluetooth address of the device",
    )
    arguments = parser.parse_args(args)

    return arguments


async def process_subscribers(cmd):
    subscribers = await youtube_subscribers(settings.CHANNEL_ID, settings.API_KEY)
    logger.debug(f"The total subscribers: {subscribers}")

    subs_str = format_subscribers(subscribers)
    logger.debug(f"The formatted total subscribers: {subs_str}")

    with tempfile.NamedTemporaryFile(mode="wb", suffix='.png') as tmp_image:
        create_subscribers_image(subs_str, Path(tmp_image.name))
        logger.debug(f"New Image generated: {tmp_image.name}")

        await cmd.image(tmp_image.name, False)
        logger.debug(f"Sent image to screen: {tmp_image.name}")


async def main():

    log_format = (
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    logging.basicConfig(
        format=log_format,
    )

    cmd = IDotMatrixScreen()

    args = parse_arguments(sys.argv[1:])

    await cmd.connect(args.address)

    while True:
        await process_subscribers(cmd)
        time.sleep(3)


if __name__ == "__main__":
    log = logging.getLogger("idotmatrix")
    log.info("initialize app")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Caught keyboard interrupt. Stopping app.")
