"""OnePlus Updates Tracker entry point"""
from importlib import import_module

from op_tracker import CONFIG

source = CONFIG.get('source')
if source == "official":
    from op_tracker.tracker_official import run
elif source == "tracker_updater":
    from op_tracker.tracker_updater import run
else:
    try:
        script = import_module(f"{__package__}.{source}")
        run = script.run()
    except ImportError:
        raise Exception("Incorrect Scraper has been specified! exiting...")

if __name__ == '__main__':
    run()
