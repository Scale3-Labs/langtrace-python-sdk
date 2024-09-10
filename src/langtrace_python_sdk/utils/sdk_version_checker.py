from importlib.metadata import version
import time
import requests
from colorama import Fore


class SDKVersionChecker:
    _cache: None
    _cache_duration: int
    _current_version: str
    _latest_version: str

    def __init__(self):
        self._cache = {"timestamp": 0, "latest_version": None}
        self._cache_duration = 3600  # Cache for 1 hour
        self._current_version = version("langtrace_python_sdk")

    def fetch_latest(self):
        try:
            current_time = time.time()
            if (
                current_time - self._cache["timestamp"] < self._cache_duration
                and self._cache["latest_version"]
            ):
                return self._cache["latest_version"]

            response = requests.get(
                "https://api.github.com/repos/Scale3-Labs/langtrace-python-sdk/releases/latest",
                timeout=20,
            )
            response.raise_for_status()
            latest_version = response.json()["tag_name"]
            self._cache.update(
                {"timestamp": current_time, "latest_version": latest_version}
            )
            self._latest_version = latest_version
            return latest_version
        except Exception as err:
            return None

    def is_outdated(self):
        latest_version = self.fetch_latest()
        if latest_version:
            return self._current_version < latest_version
        return False

    def get_sdk_version(self):
        return self._current_version

    def check(self):
        if self.is_outdated():
            print(
                Fore.YELLOW
                + f"Warning: Your Langtrace SDK version {self._current_version} is outdated. Please upgrade to {self._latest_version}."
                + Fore.RESET
            )
