import json
import io
import os
import requests
from typing import Iterator, Literal, Union
from colorama import Fore
from langtrace_python_sdk.constants.exporter.langtrace_exporter import (
    LANGTRACE_REMOTE_URL,
)
from fsspec.spec import AbstractFileSystem

OpenTextMode = Literal["r", "a", "w"]
OpenBinaryMode = Literal["rb", "ab", "wb"]


class OpenMode(str):
    def __init_subclass__(cls, **kwargs):
        allowed_values = Union[set(OpenTextMode.__args__), set(OpenBinaryMode.__args__)]
        super().__init_subclass__(**kwargs)

        def __new__(cls, value):
            if value not in allowed_values:
                raise ValueError(f"Invalid value for OpenMode: {value}")
            return super().__new__(cls, value)

        cls.__new__ = __new__


class LangTraceFile(io.BytesIO):

    def __init__(self, fs: "LangTraceFileSystem", path: str, mode: OpenMode):
        super().__init__()
        self.fs = fs
        self.path = path
        self.mode = mode
        self._host: str = os.environ.get("LANGTRACE_API_HOST", LANGTRACE_REMOTE_URL)
        self._api_key: str = os.environ.get("LANGTRACE_API_KEY", None)
        if self._host.endswith("/api/trace"):
            self._host = self._host.replace("/api/trace", "")

        if self._api_key is None:
            print(Fore.RED)
            print(
                f"Missing Langtrace API key, proceed to {self._host} to create one"
            )
            print("Set the API key as an environment variable LANGTRACE_API_KEY")
            print(Fore.RESET)
            return

    def close(self) -> None:
        if not self.closed:
            self.seek(0)
            file_data = self.getvalue()
            self.fs.files[self.path] = file_data

            # Upload the file to the remote server
            self.upload_to_server(file_data)

        super().close()

    def upload_to_server(self, file_data: bytes) -> None:
        try:
            # Parse the log file and upload it to the server
            log = file_data.decode("utf-8")
            eval_log = json.loads(log)
            data = {
                "runId": eval_log["eval"]["run_id"],
                "taskId": eval_log["eval"]["task_id"],
                "log": log,
            }
            if self.path is not None:
                dataset_id = self.path.split("/")[0]
                print(
                    Fore.GREEN
                    + f"Sending results to Langtrace for dataset: {dataset_id}"
                    + Fore.RESET
                )
                data["datasetId"] = dataset_id
            else:
                print(Fore.GREEN + "Sending results to Langtrace" + Fore.RESET)
            response = requests.post(
                url=f"{self._host}/api/run",
                data=json.dumps(data),
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self._api_key,
                },
                timeout=20,
            )
            response.raise_for_status()
            print(Fore.GREEN + "Results sent to Langtrace successfully." + Fore.RESET)
        except requests.exceptions.RequestException as error:
            print(Fore.RED + f"Error reporting results: {error}" + Fore.RESET)


class LangTraceFileSystem(AbstractFileSystem):
    protocol = "langtracefs"
    sep = "/"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = {}
        self.dirs = set()
        self._host: str = os.environ.get("LANGTRACE_API_HOST", LANGTRACE_REMOTE_URL)
        self._api_key: str = os.environ.get("LANGTRACE_API_KEY", None)
        if self._host.endswith("/api/trace"):
            self._host = self._host.replace("/api/trace", "")

        if self._api_key is None:
            print(Fore.RED)
            print(
                f"Missing Langtrace API key, proceed to {self._host} to create one"
            )
            print("Set the API key as an environment variable LANGTRACE_API_KEY")
            print(Fore.RESET)
            return

    def open(
        self,
        path: str,
        mode: Union[OpenTextMode, OpenBinaryMode] = "rb",
        **kwargs,
    ) -> Iterator[Union[LangTraceFile, io.BytesIO]]:
        if "r" in mode:
            dataset_id = path
            # Fetch file from API and return a BytesIO object
            file_data = self.fetch_file_from_api(dataset_id)
            return io.BytesIO(file_data)
        elif "w" in mode or "a" in mode:
            return LangTraceFile(self, path, mode)
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    def fetch_file_from_api(self, dataset_id: str) -> bytes:
        try:
            print(
                Fore.GREEN
                + f"Fetching dataset with id: {dataset_id} from Langtrace"
                + Fore.RESET
            )
            response = requests.get(
                url=f"{self._host}/api/dataset/download?id={dataset_id}",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self._api_key,
                },
                timeout=20,
            )
            print(
                Fore.GREEN
                + f"Successfully fetched dataset with id: {dataset_id} from Langtrace"
                + Fore.RESET
            )
            response.raise_for_status()
            file_data = response.content
            return file_data
        except requests.exceptions.RequestException as error:
            print(
                Fore.RED
                + f"Error fetching dataset with id: {dataset_id} from Langtrace: {error}"
                + Fore.RESET
            )
            return b""

    def makedirs(self, path: str, exist_ok: bool = False) -> None:
        if not exist_ok and path in self.dirs:
            raise FileExistsError(f"Directory {path} already exists")
        self.dirs.add(path)

    def info(self, path: str, **kwargs):
        if path in self.files:
            return {"name": path, "size": len(self.files[path]), "type": "file"}
        elif path in self.dirs:
            return {"name": path, "type": "directory"}
        else:
            raise FileNotFoundError(f"No such file or directory: {path}")

    def created(self, path: str) -> float:
        # Return a dummy creation time
        return 0.0

    def exists(self, path: str) -> bool:
        return path in self.files or path in self.dirs

    def ls(self, path: str, detail: bool = False, **kwargs):
        if path not in self.dirs:
            raise FileNotFoundError(f"No such directory: {path}")
        entries = []
        for file_path in self.files:
            if file_path.startswith(path + self.sep):
                if detail:
                    entries.append(self.info(file_path))
                else:
                    entries.append(file_path)
        for dir_path in self.dirs:
            if dir_path.startswith(path + self.sep):
                if detail:
                    entries.append(self.info(dir_path))
                else:
                    entries.append(dir_path)
        return entries

    def walk(self, path: str, maxdepth: int = None, **kwargs):
        for root, dirs, files in self._walk(path):
            yield root, dirs, [self.sep.join([root, f]) for f in files]

    def _walk(self, path: str):
        if path in self.dirs:
            dirs = [d for d in self.dirs if d.startswith(path + self.sep)]
            files = [f for f in self.files if f.startswith(path + self.sep)]
            yield path, [d.split(self.sep)[-1] for d in dirs], [
                f.split(self.sep)[-1] for f in files
            ]
            for d in dirs:
                yield from self._walk(d)

    def unstrip_protocol(self, path: str) -> str:
        return path

    def invalidate_cache(self, path: str = None) -> None:
        pass
