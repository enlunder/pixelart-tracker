### iDotMatrix YouTube Subscriber Counter

This project uses Python to display the number of subscribers of a YouTube channel on a 32px by 32px iDotMatrix-style pixel art screen.

**Dependencies:**

-   Python 3.x
-   asyncio
-   aiohttp
-   PIL (Pillow) 10.x
-   idotmatrix 0.0.4
-   PyDantic 1.10.x
-   uvicorn
-   fastapi

**Installation:**

1.  Install the python package:

```
pip install pixelart-tracker

```

1.1 Or run it without installing (add the same arguments as under Usage below):

```
python -c "from src.pixeltracker.app import main;main()" 
```

2.  Get your Youtube API KEY:
Request an API KEY going here https://console.cloud.google.com/apis/api/youtube.googleapis.com/credentials

3.  Set env variables:

```
export SUBS_YOUTUBE_CHANNEL_ID=YOUR_YOUTUBE_CHANNEL_ID
export SUBS_YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY

```


**Usage:**

1.  Scan for compatible devices:

```
pix-track --scan

```

2.  Run on device:

```
pix-track --address <device_mac_address>/auto

```

Where `<device_mac_address>` is the device physical address or `auto` is to autodiscover devices and use the first one found.

**Example:**

```
pix-track --address 37:D4:98:8F:2B:C8

```

3.  This version includes a web server available listening at all interfaces at port 9191

Try visiting `http://localhost:9191/docs/` in your browser.


**Code Explanation:**

-   The script uses the `aiohttp` library to get the YouTube channel information.
-   The channel information is parsed into a dictionary.
-   The subscriber count is extracted from the dictionary.
-   The subscriber count is converted to a pixel readable string.
-   The string is converted to a character array.
-   The character array is used to create a pixel art image.
-   The pixel art image is displayed on the screen.

**Technical Details:**

-   The iDotMatrix display is simulated using the `PIL (Pillow)` library.
-   The total screen size is 32px by 32px pixels.
-   The pixels are colored always white for the characters.
-   The pixel art image is scaled to fit the screen.

**License:**

This project is licensed under the MIT license.

**Contributions:**

Contributions to this project are welcome. Create an issue or pull request on GitHub to get started.
