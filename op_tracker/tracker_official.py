"""
OnePlus Updates Tracker main module
This module is the entry point for the tracker script and contains the controller part
"""
import asyncio
import logging
from dataclasses import asdict

from op_tracker import WORK_DIR, CONFIG
from op_tracker.common.database.helpers import export_latest
from op_tracker.official.api_client.api_client import APIClient
from op_tracker.official.models.device import Device
from op_tracker.utils.data_manager import DataManager
from op_tracker.utils.git import git_commit_push
from op_tracker.utils.telegram import TelegramBot

logger = logging.getLogger(__name__)


async def check_update(device: Device, region, api):
    """Asynchronously checks device updates"""
    updates: list = await api.get_updates(device, region)
    logger.debug(updates)
    return [i for i in updates] if updates else None


async def main():
    """Main function"""
    logger = logging.getLogger(__name__)
    new_updates: list = []
    regions = DataManager.read_file(f"{WORK_DIR}/data/official/regions.yml")
    for region in regions:
        region_code = region.get("code")
        logger.info(f"Fetching {region_code}")
        api: APIClient = APIClient(region_code)
        devices: list = await api.get_devices()
        logger.debug(f"{region_code} devices: {devices}")
        DataManager.write_file(
            f"{WORK_DIR}/data/official/{region_code}/{region_code}.yml",
            [asdict(i) for i in devices])
        tasks = [asyncio.ensure_future(check_update(device, region, api))
                 for device in api.devices]
        results = await asyncio.gather(*tasks)
        for result in results:
            if result:
                new_updates.append(result[0])
        await api.close()
    if new_updates:
        logger.info(f"New updates: {new_updates}")
        bot: TelegramBot = TelegramBot(
            CONFIG.get('tg_bot_token'), CONFIG.get('tg_chat'), "website")
        bot.post_updates(new_updates)
    export_latest()
    await git_commit_push()


def run():
    """asyncio trigger function"""
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
