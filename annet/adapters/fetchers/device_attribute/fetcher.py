from collections.abc import Iterable
from typing import Any

from annet.connectors import AdapterWithConfig, AdapterWithName
from annet.deploy import Fetcher
from annet.storage import Device


class DeviceAttributeFetcher(Fetcher, AdapterWithConfig, AdapterWithName):
    def __init__(self, running_config_attribute: str | Iterable[str] | None = None) -> None:
        if running_config_attribute is None:
            running_config_attribute = ("running_config", "running-config")
        elif isinstance(running_config_attribute, str):
            running_config_attribute = (running_config_attribute,)
        self.running_config_attributes = tuple(running_config_attribute)

    @classmethod
    def name(cls) -> str:
        return "device_attribute"

    @classmethod
    def with_config(cls, **kwargs: dict[str, Any]) -> Fetcher:
        return cls(**kwargs)

    async def fetch_packages(
        self,
        devices: list[Device],
        processes: int = 1,
        max_slots: int = 0,
    ) -> tuple[dict[Device, str], dict[Device, Any]]:
        return {}, {}

    async def fetch(
        self,
        devices: list[Device],
        files_to_download: dict[Device, list[str]] | None = None,
        processes: int = 1,
        max_slots: int = 0,
    ):
        if files_to_download is not None:
            return self._fetch_files(devices, files_to_download)
        return self._fetch_running_config(devices)

    def _fetch_running_config(self, devices: list[Device]) -> tuple[dict[Device, str], dict[Device, Exception]]:
        configs: dict[Device, str] = {}
        failed: dict[Device, Exception] = {}
        for device in devices:
            try:
                configs[device] = self._get_first_device_attribute(device, self.running_config_attributes)
            except Exception as exc:  # pylint: disable=broad-except
                failed[device] = exc
        return configs, failed

    def _fetch_files(
        self,
        devices: list[Device],
        files_to_download: dict[Device, list[str]],
    ) -> tuple[dict[Device, dict[str, str | None]], dict[Device, Exception]]:
        files: dict[Device, dict[str, str | None]] = {}
        failed: dict[Device, Exception] = {}
        for device in devices:
            try:
                device_files = {}
                for path in files_to_download.get(device, []):
                    try:
                        device_files[path] = self._get_device_attribute(device, path)
                    except AttributeError:
                        device_files[path] = None
                files[device] = device_files
            except Exception as exc:  # pylint: disable=broad-except
                failed[device] = exc
        return files, failed

    @staticmethod
    def _get_device_attribute(device: Device, name: str) -> str:
        value = getattr(device, name)
        if not isinstance(value, str):
            raise TypeError(f"Device attribute {name!r} must be str, got {type(value).__name__}")
        return value

    @classmethod
    def _get_first_device_attribute(cls, device: Device, names: Iterable[str]) -> str:
        missing = []
        for name in names:
            try:
                return cls._get_device_attribute(device, name)
            except AttributeError:
                missing.append(name)
        raise AttributeError(f"Device has none of the config attributes: {', '.join(repr(name) for name in missing)}")
