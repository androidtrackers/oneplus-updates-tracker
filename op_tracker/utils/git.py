import logging
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE, Process
from datetime import datetime

from op_tracker import CONFIG, WORK_DIR


async def git_commit_push():
    command: str = f'git add {WORK_DIR}/data/*.yml {WORK_DIR}/data/*/*.yml {WORK_DIR}/data/*/*/*.yml && ' \
                   f'git -c "user.name=CI" -c "user.email=CI@example.com" ' \
                   f'commit -m "sync: {datetime.today().strftime("%d-%m-%Y %H:%M:%S")}" && ' \
                   f'git push -q https://{CONFIG.get("git_oauth_token")}@github.com/androidtrackers/' \
                   f'oneplus-updates-tracker.git HEAD:master'
    process: Process = await create_subprocess_shell(command, stdin=PIPE, stdout=PIPE)
    await process.wait()
    if process.returncode != 0 and process.returncode != 1:
        stdout = await process.stdout.read()
        logger = logging.getLogger(__name__)
        logger.warning(f"Cannot commit and push changes! Error code: {process.returncode}\n"
                       f"Output: {stdout.decode()}")
