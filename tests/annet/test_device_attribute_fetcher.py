import pytest

from annet.adapters.fetchers.device_attribute.fetcher import DeviceAttributeFetcher


class FakeDevice:
    def __hash__(self):
        return id(self)


def run(coro):
    try:
        import asyncio

        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)


def test_fetch_reads_running_config_attribute():
    device = FakeDevice()
    device.running_config = "hostname test"
    fetcher = DeviceAttributeFetcher()

    configs, failed = run(fetcher.fetch([device]))

    assert configs == {device: "hostname test"}
    assert failed == {}


def test_fetch_reads_running_config_attribute_with_dash():
    device = FakeDevice()
    setattr(device, "running-config", "hostname dash")
    fetcher = DeviceAttributeFetcher()

    configs, failed = run(fetcher.fetch([device]))

    assert configs == {device: "hostname dash"}
    assert failed == {}


def test_fetch_reads_configured_attribute_name():
    device = FakeDevice()
    device.config = "hostname custom"
    fetcher = DeviceAttributeFetcher(running_config_attribute="config")

    configs, failed = run(fetcher.fetch([device]))

    assert configs == {device: "hostname custom"}
    assert failed == {}


def test_fetch_reports_missing_attribute():
    device = FakeDevice()
    fetcher = DeviceAttributeFetcher(running_config_attribute="config")

    configs, failed = run(fetcher.fetch([device]))

    assert configs == {}
    assert isinstance(failed[device], AttributeError)


def test_fetch_reports_non_string_attribute():
    device = FakeDevice()
    device.running_config = {"hostname": "test"}
    fetcher = DeviceAttributeFetcher()

    configs, failed = run(fetcher.fetch([device]))

    assert configs == {}
    assert isinstance(failed[device], TypeError)
    assert "must be str" in str(failed[device])


@pytest.mark.parametrize("file_content", ["{}", None])
def test_fetch_files_reads_file_path_attributes(file_content):
    device = FakeDevice()
    if file_content is not None:
        setattr(device, "/etc/config.json", file_content)
    fetcher = DeviceAttributeFetcher()

    files, failed = run(fetcher.fetch([device], files_to_download={device: ["/etc/config.json"]}))

    assert files == {device: {"/etc/config.json": file_content}}
    assert failed == {}
