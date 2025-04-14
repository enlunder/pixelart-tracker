import argparse
import asyncio
import logging
import sys
import time

import colorlog

# idotmatrix imports
from .screen import IDotMatrixScreen
from .settings import settings
from .tiles import Crypto, YoutubeViewers, Message, Finance

from fastapi import FastAPI, BackgroundTasks, UploadFile, File, status, Request
from fastapi.exceptions import HTTPException
import os
import signal
import shutil
import uvicorn

PORT = 9191 # :TODO: move to settings


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

server_app = FastAPI()
message_queue = asyncio.Queue()

# Define a route for receiving messages
@server_app.post("/message")
async def receive_message(message: str):
    await message_queue.put(message)
    return {"message": "Received"}

# Define a function to run the FastAPI server
async def run_server():
    import uvicorn
    config = uvicorn.Config(server_app, host="0.0.0.0", port=9191)
    server = uvicorn.Server(config)
    await server.serve()

async def show_message(idms, message_tile):
    while True:
        run_tile_task = asyncio.create_task(message_tile.run())
        await run_tile_task

        # Pre-defined text-speed, will vary with font and text speed settings
        chars_per_second = 6.912/26
        
        # Set a delay to enable showing the received message twice
        delay = 2.0*chars_per_second*len(message_tile.message)
        
        if delay < 7: # Show each message at least 7 seconds
            delay = 7
        elif delay > 60: # Don't show any message more than 60 seconds
            delay = 60

        # Wait for 5 seconds and check for new messages
        start_time = asyncio.get_running_loop().time()
        try:
            new_message = await asyncio.wait_for(message_queue.get(), timeout=5)
            new_message = new_message[:80]
            new_message_tile = Message(idms, new_message, test = False)
            del message_tile
            message_tile = new_message_tile
        except asyncio.TimeoutError:
            # No new message arrived, calculate the remaining time and sleep
            elapsed_time = asyncio.get_running_loop().time() - start_time
            remaining_time = delay - elapsed_time
            if remaining_time > 0:
                await asyncio.sleep(remaining_time)
            break
        message_queue.task_done()

    
async def run():
    idms = IDotMatrixScreen()

    args = parse_arguments(sys.argv[1:])

    if args.scan:
        await idms.scan()
        quit()

    await idms.connect(args.address)

    await idms.reset()

    server_task = asyncio.create_task(run_server())
    
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
#                tiles.append(instance)
        elif tile == "finance":
            finance_tiles = str(settings.FINANCE_TICKERS).split(",")
            for finance_tile in finance_tiles:
                instance = Finance(idms, finance_tile, args.test)
                tiles.append(instance)
            
    what_tile = 0

    while True:
        if message_queue.empty():
            # Run a tile if there are no messages
            run_tile_task = asyncio.create_task(tiles[what_tile % len(tiles)].run())
            what_tile = what_tile + 1 # next tile on the next run... 
            try:
                # Wait for 30 seconds or until a message arrives
                message = await asyncio.wait_for(message_queue.get(), timeout=30)
                
                # Cancel the tile task if a message arrives
                run_tile_task.cancel()
                
                # Can't send message to screen if larger than 80 to 88
                # characters Perhaps need to wait for responses in the
                # idotmatrix text module where we chunk?
                # I.e. around self.conn.send(data=chunk)
                message = message[:80]
                message_tile = Message(idms, message, test = False)
            
                await show_message(idms, message_tile)
                del message_tile
            except asyncio.TimeoutError:
                print("no message arrived within 30 seconds")
                pass
        else:
            await asyncio.sleep(0.1)
            # Get the message from the queue
            message = await message_queue.get()
            message = message[:80]
            message_tile = Message(idms, message, test = False)
            await show_message(idms, message_tile)

    await server_task

def main():
    
    log_format = "%(asctime)s | %(levelname)s | %(message)s"
    logging.basicConfig(
        format=log_format,
    )
    logger = logging.getLogger("pixelart-tracker")

    stdout = colorlog.StreamHandler(stream=sys.stdout)

    fmt = colorlog.ColoredFormatter(
        "%(name)s: %(white)s%(asctime)s%(reset)s | %(log_color)s%(levelname)s%(reset)s | %(blue)s%(filename)s:%(lineno)s%(reset)s | %(process)d >>> %(log_color)s%(message)s%(reset)s"
    )

    stdout.setFormatter(fmt)
    logger.addHandler(stdout)
    
    logger.setLevel(settings.LOG_LEVEL)
    logger.info("initialize app")

    logging.getLogger("idotmatrix").setLevel(settings.LOG_LEVEL)
    logging.getLogger('PIL').setLevel(settings.LOG_LEVEL)
    logging.getLogger("asyncio").setLevel(settings.LOG_LEVEL)
    logging.getLogger("yfinance").setLevel(settings.LOG_LEVEL)
    logging.getLogger("urllib3").setLevel(settings.LOG_LEVEL)
    logging.getLogger("peewee").setLevel(settings.LOG_LEVEL)        
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Caught keyboard interrupt. Stopping app.")
        

