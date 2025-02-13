import sys
import json
import pathlib
import time
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Union

import psutil


@dataclass(frozen=True)
class ConfigEnv:
    env: str
    kv_name: str
    st_account: str
    google_region_name: str
    google_project_id: str


def read_env(
    file: Union[str, pathlib.Path],
    *,
    encoding: str = "utf8",
) -> ConfigEnv:
    with open(file, "r", encoding=encoding) as f:
        config: dict[str, str] = {
            k.replace("-", "_"): str(v)
            for k, v in json.load(f).items()
        }
    return ConfigEnv(**config)


def read_extended_prop() -> dict[str, Any]:
    with open('./activity.json', "r", encoding='utf-8') as f:
        properties = json.load(f)
    return properties.get('typeProperties', {}).get('extendedProperties', {})


def write_output(data: dict[str, Any]) -> None:
    with open('./outputs.json', mode='wt', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


class MonitorThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.

    :param event: A threading event object for trigger if you want to stop.
    """

    def __init__(self, event, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.event = event
        print(
            f"[DEBUG]: Setup monitoring thread with event: {event}: {event.is_set()}")

    def run(self) -> None:
        """ main control loop """
        while not self.event.is_set():
            print(
                f"[DEBUG]: {datetime.now():%Y-%m-%d %H:%M:%S} "
                f"CPU %: {psutil.cpu_percent()}, "
                f"Mem %: {psutil.virtual_memory().percent}, "
                f"Thread: {threading.active_count()}, "
                f"Process: {len([*psutil.process_iter()])}"
            )
            time.sleep(15)
        print('[DEBUG]: Monitoring thread already stopped')


def run_monitoring(main_func: callable):
    event = threading.Event()
    thread = MonitorThread(event=event)
    thread.start()

    try:
        returning = main_func()
    except Exception as error:
        print(f"Error Handler of main func: {error}", file=sys.stderr)
        returning = error

    event.set()
    thread.join()
    if returning is not None:
        raise returning
    sys.exit(0)
