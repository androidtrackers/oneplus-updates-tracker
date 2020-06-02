"""OnePlus Updates Tracker entry point"""
from op_tracker import CONFIG

if CONFIG.get('source') == "official":
    from op_tracker.tracker_official import run
else:
    raise Exception("Incorrect Scraper has been specified! exiting...")

if __name__ == '__main__':
    run()
