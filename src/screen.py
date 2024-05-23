
import logging
from pathlib import Path

from PIL import Image

# idotmatrix imports
from idotmatrix import ConnectionManager
from idotmatrix import Image


class IDotMatrixScreen:
    conn = ConnectionManager()
    logging = logging.getLogger("idotmatrix." + __name__)

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

    async def image(self, image_path: Path, process_image: bool):
        """enables or disables the image mode and uploads a given image file"""
        self.logging.info("setting image")
        image = Image()
        await image.setMode(
            mode=1,
        )
        if image_path:
            if process_image:
                await image.uploadProcessed(
                    file_path=str(image_path),
                    pixel_size=int(process_image),
                )
            else:
                await image.uploadUnprocessed(
                    file_path=str(image_path),
                )
