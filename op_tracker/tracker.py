import asyncio
import logging
import yaml
from dataclasses import asdict

from op_tracker import WORK_DIR, CONFIG
from op_tracker.official.models.device import Device
from op_tracker.official.models.devices import Devices
from op_tracker.official.models.update import Update
from op_tracker.official.scrapers.base_website import Scraper
from op_tracker.utils.data_manager import DataManager
from op_tracker.utils.git import git_commit_push
from op_tracker.utils.merger import merge_devices, merge_updates
from op_tracker.utils.telegram import TelegramBot


async def main():
    logger = logging.getLogger(__name__)
    new_updates: list = []
    with open(f"{WORK_DIR}/data/regions.yml", "r") as yaml_file:
        regions: dict = yaml.load(yaml_file, Loader=yaml.FullLoader)
    for region_code, region in regions.items():
        logger.info(f"Fetching {region_code}")
        website: Scraper = Scraper(region_code)
        await website.get_devices()
        devices: Devices = Devices.from_response(website.devices)
        logger.info(f"{region} devices: {devices.items}")
        devices_fm: DataManager = DataManager(devices.items, f"{WORK_DIR}/data/{region_code}/{region_code}.yml")
        devices_fm.backup()
        devices_fm.save()
        new_devices: dict = devices_fm.diff_dicts()
        if new_devices:
            logging.info(f"New device(s) added: {new_devices}")
            devices_fm.write_file(f"{WORK_DIR}/data/{region_code}/{region_code}.changes", new_devices)
        for item in website.devices:
            device: Device = Device.from_response(item)
            updates: list = await website.get_updates(device)
            for update_data in updates:
                update: Update = Update.from_response(update_data, region)
                logger.debug(update)
                device_fm: DataManager = DataManager(
                    asdict(update), f"{WORK_DIR}/data/{region_code}/{update.type}/{update.device}.yml")
                device_fm.backup()
                device_fm.save()
                if device_fm.is_new_version():
                    new_updates.append(update)
        await website.close()
    if new_updates:
        logger.info(f"New updates: {new_updates}")
        bot: TelegramBot = TelegramBot(CONFIG.get('tg_bot_token'), CONFIG.get('tg_chat'))
        bot.post_updates(new_updates)
    devices: list = merge_devices(regions)
    merge_updates(devices)
    await git_commit_push()


def run():
    """Main"""
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
