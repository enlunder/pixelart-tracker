import sys
import tempfile
import time
from pathlib import Path
from random import randrange

import argparse
import asyncio
import logging

# idotmatrix imports
from screen import IDotMatrixScreen

from settings import settings
from youtube import youtube_subscribers, format_subscribers, create_subscribers_image

logger = logging.getLogger(__name__)


test_subscribers = 0


def parse_arguments(args):
    parser = argparse.ArgumentParser(
        description="control your 16x16 or 32x32 pixel displays"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scans all bluetooth devices in range for iDotMatrix displays",
    )
    parser.add_argument(
        "--address",
        action="store",
        help="Bluetooth address of the device to connect",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Fake subscribers numbers on every refresh to show bigger numbers",
    )
    arguments = parser.parse_args(args)

    return arguments


async def format_and_send_to_screen(idms: IDotMatrixScreen, subscribers):
    subs_str = format_subscribers(subscribers)
    logger.debug(f"The formatted total subscribers: {subs_str}")

    with tempfile.NamedTemporaryFile(mode="wb", suffix='.png') as tmp_image:
        create_subscribers_image(subs_str, Path(tmp_image.name))
        logger.debug(f"New Image generated: {tmp_image.name}")

        await idms.set_image(Path(tmp_image.name), False)
        logger.debug(f"Sent image to screen: {tmp_image.name}")


async def process_subscribers(idms: IDotMatrixScreen):
    subscribers = await youtube_subscribers(settings.CHANNEL_ID, settings.API_KEY)
    logger.debug(f"The total subscribers: {subscribers}")

    await format_and_send_to_screen(idms, subscribers)


async def fake_subscribers(idms: IDotMatrixScreen):
    global test_subscribers
    await format_and_send_to_screen(idms, test_subscribers)

    test_subscribers = test_subscribers + randrange(1000)


async def main():

    log_format = (
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    logging.basicConfig(
        format=log_format,
    )

    idms = IDotMatrixScreen()

    args = parse_arguments(sys.argv[1:])

    if args.scan:
        await idms.scan()
        quit()

    await idms.connect(args.address)

    while True:
        if args.test:
            await fake_subscribers(idms)
        else:
            await process_subscribers(idms)
        time.sleep(settings.REFRESH_TIME)


if __name__ == "__main__":
    log = logging.getLogger("idotmatrix")
    log.info("initialize app")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Caught keyboard interrupt. Stopping app.")
