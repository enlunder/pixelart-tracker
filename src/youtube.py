import aiohttp
import logging

from settings import settings


logger = logging.getLogger(__name__)


async def get_json(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def youtube_subscribers(channel_id: str, api_key: str) -> int:
    yt_api_url = settings.API_HOST
    url = f"{yt_api_url}&id={channel_id}&key={api_key}"

    response = await get_json(url)
    subscribers = response["items"][0]["statistics"]["subscriberCount"]
    return int(subscribers)

