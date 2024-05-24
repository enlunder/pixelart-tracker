import argparse
import asyncio
import logging
import sys
import time

import colorlog

# idotmatrix imports
from .screen import IDotMatrixScreen
from .settings import settings
from .tiles import Crypto, YoutubeViewers

test_subscribers = 0


def parse_arguments(args):
    parser = argparse.ArgumentParser(description="control your 16x16 or 32x32 pixel displays")
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
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
        default=logging.WARNING,
    )
    arguments = parser.parse_args(args)

    return arguments


async def run():
    idms = IDotMatrixScreen()

    args = parse_arguments(sys.argv[1:])

    if args.scan:
        await idms.scan()
        quit()

    await idms.connect(args.address)

    tile_collection = str(settings.TILES).split(",")
    tiles = []
    for tile in tile_collection:
        if tile == "yt":
            instance = YoutubeViewers(idms, args.test)
            tiles.append(instance)
        elif tile == "crypto":
            crypto_tiles = str(settings.CRYPTO_CURRENCIES).split(",")
            for crypto_tile in crypto_tiles:
                instance = Crypto(idms, crypto_tile, args.test)
                tiles.append(instance)

    while True:
        for tile in tiles:
            await tile.run()
            time.sleep(settings.REFRESH_TIME)


def main():
    log_format = "%(asctime)s | %(levelname)s | %(message)s"
    logging.basicConfig(
        format=log_format,
    )
    logger = logging.getLogger(__name__)

    stdout = colorlog.StreamHandler(stream=sys.stdout)

    fmt = colorlog.ColoredFormatter(
        "%(name)s: %(white)s%(asctime)s%(reset)s | %(log_color)s%(levelname)s%(reset)s | %(blue)s%(filename)s:%(lineno)s%(reset)s | %(process)d >>> %(log_color)s%(message)s%(reset)s"
    )

    stdout.setFormatter(fmt)
    logger.addHandler(stdout)

    logger.setLevel(logging.WARNING)
    logger.info("initialize app")
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Caught keyboard interrupt. Stopping app.")
