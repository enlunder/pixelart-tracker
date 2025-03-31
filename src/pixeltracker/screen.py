import logging
from pathlib import Path
from typing import Optional

# idotmatrix imports
from idotmatrix import ConnectionManager, Image, Text, Clock

class IDotMatrixScreen:
    conn = ConnectionManager()
    logging = logging.getLogger("pixelart-tracker")
    
    image: Optional[Image] = None
    text: Optional[Text] = None
    clock: Optional[Clock] = None    
    
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

    async def set_clock(self):
        """shows a specific clock"""
        self.logging.info("setting clock") 
        if not self.clock:
            self.clock = Clock()
        
        await self.clock.setMode(
            style=1
        )
            
    async def set_text(self, text, font_path):
        """shows a specific text"""
        self.logging.info("setting text")
        self.clock = None # If I don't zero these out the screen stops reacting to inputs
        self.image = None

        if not self.text:
            self.text = Text()

        await self.text.setMode(
            text,
            font_size=16,
            speed=100,
            text_color_mode=2, 
            font_path=font_path
        )
