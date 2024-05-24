import sys
import time

import argparse
import asyncio
import logging

# idotmatrix imports
from screen import IDotMatrixScreen

from settings import settings
from tiles import YoutubeViewers, Crypto

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


if __name__ == "__main__":
    log = logging.getLogger("idotmatrix")
    log.info("initialize app")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Caught keyboard interrupt. Stopping app.")
