import logging
from pathlib import Path
from typing import Optional

# idotmatrix imports
from idotmatrix import ConnectionManager, Image


class IDotMatrixScreen:
    conn = ConnectionManager()
    logging = logging.getLogger("pixelart-tracker")
    image: Optional[Image] = None

    async def scan(self):
        await self.conn.scan()
        quit()

    async def connect(self, address: str):
        self.logging.info("initializing command line")
        if address:
            self.logging.debug("using --address")
        if address is None:
            self.logging.error("no device address given")
            quit()
        elif str(address).lower() == "auto":
            await self.conn.connectBySearch()
        else:
            await self.conn.connectByAddress(address)

    async def set_image(self, image_path: Path, process_image: bool):
        """enables or disables the image mode and uploads a given image file"""
        self.logging.info("setting image")
        if not self.image:
            self.image = Image()
            await self.image.setMode(
                mode=1,
            )

        if image_path:
            if process_image:
                await self.image.uploadProcessed(
                    file_path=str(image_path),
                    pixel_size=int(process_image),
                )
            else:
                await self.image.uploadUnprocessed(
                    file_path=str(image_path),
                )
