"""
OnePlus Updates Tracker main module
This module is the entry point for the tracker script and contains the controller part
"""
import asyncio
import logging
from dataclasses import asdict

from op_tracker import WORK_DIR
from op_tracker.official.api_client.api_client import APIClient
from op_tracker.official.models.device import Device
from op_tracker.official.models.devices import Devices
from op_tracker.official.models.update import Update
from op_tracker.utils.data_manager import DataManager
from op_tracker.utils.git import git_commit_push
from op_tracker.utils.merger import merge_devices, merge_updates


async def check_update(item, region, region_code, api, logger):
    """Asynchronously checks device updates"""
    new_updates = []
    device: Device = Device.from_response(item)
    updates: list = await api.get_updates(device)
    for update_data in updates:
        update: Update = Update.from_response(update_data, region)
        logger.debug(update)
        device_fm: DataManager = DataManager(
            asdict(update),
            f"{WORK_DIR}/data/official/{region_code}/{update.type}/{update.device}.yml")
        device_fm.backup()
        device_fm.save()
        if device_fm.is_new_version():
            new_updates.append(update)
        if new_updates:
            return new_updates


async def main():
    """Main function"""
    logger = logging.getLogger(__name__)
    new_updates: list = []
    regions = DataManager.read_file(f"{WORK_DIR}/data/official/regions.yml")
    for region_code, region in regions.items():
        logger.info(f"Fetching {region_code}")
        api: APIClient = APIClient(region_code)
        await api.get_devices()
        devices: Devices = Devices.from_response(api.devices)
        logger.info(f"{region} devices: {devices.items}")
        devices_fm: DataManager = DataManager(
            devices.items,
            f"{WORK_DIR}/data/official/{region_code}/{region_code}.yml")
        devices_fm.backup()
        devices_fm.save()
        new_devices: dict = devices_fm.diff_dicts()
        if new_devices:
            logging.info(f"New device(s) added: {new_devices}")
            devices_fm.write_file(
                f"{WORK_DIR}/data/official/{region_code}/{region_code}.changes",
                new_devices)
        tasks = [asyncio.ensure_future(check_update(item, region, region_code, api, logger))
                 for item in api.devices]
        results = await asyncio.gather(*tasks)
        for result in results:
            if result:
                new_updates.append(result[0])
        await api.close()
    # if new_updates:
    #     logger.info(f"New updates: {new_updates}")
    #     bot: TelegramBot = TelegramBot(
    #         CONFIG.get('tg_bot_token'), CONFIG.get('tg_chat'), "official")
    #     bot.post_updates(new_updates)
    devices: list = merge_devices(regions)
    merge_updates(devices)
    await git_commit_push()


def run():
    """asyncio trigger function"""
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
