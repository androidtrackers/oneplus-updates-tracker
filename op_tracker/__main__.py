"""OnePlus Updates Tracker entry point"""
from importlib import import_module

from op_tracker import CONFIG
from op_tracker.tracker_official import run as official

source = CONFIG.get('source')

if source == "tracker_updater":
    from op_tracker.tracker_updater import run as extra_run
else:
    try:
        script = import_module(f"{__package__}.{source}")
        extra_run = script.run()
    except ImportError:
        raise Exception("Incorrect Scraper has been specified! exiting...")

if __name__ == '__main__':
    if extra_run:
        extra_run()
    official()
