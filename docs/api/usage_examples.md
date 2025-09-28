# Annet API Usage Examples

## Overview

This document provides comprehensive usage examples for all major Annet APIs, demonstrating common patterns and best practices for network configuration management.

## Table of Contents

1. [Basic Setup and Initialization](#basic-setup-and-initialization)
2. [Device Management](#device-management)
3. [Configuration Generation](#configuration-generation)
4. [Configuration Deployment](#configuration-deployment)
5. [Configuration Diffing and Patching](#configuration-diffing-and-patching)
6. [Rulebook Management](#rulebook-management)
7. [Storage Integration](#storage-integration)
8. [Advanced Patterns](#advanced-patterns)
9. [Error Handling](#error-handling)
10. [Performance Optimization](#performance-optimization)

## Basic Setup and Initialization

### Initialize Annet Framework

```python
import annet
from annet.argparse import ArgParser
from annet.cli_args import DeployOptions

# Initialize Python version check
annet.assert_python_version()

# Create argument parser
parser = ArgParser()

# Add base arguments
annet.fill_base_args(parser, "annet", "configs/logging.yaml")

# Parse arguments
args = parser.parse_args([
    "--log-level", "INFO",
    "router1", "router2"
])

# Initialize annet
annet.init(args)
```

### Set Up Connectors

```python
from annet import rulebook, hardware, diff
from annet.rulebook import DefaultRulebookProvider
from annet.hardware import AnnetHardwareProvider
from annet.diff import UnifiedFileDiffer

# Set up rulebook provider
rulebook.rulebook_provider_connector.set(DefaultRulebookProvider())

# Set up hardware provider
hardware.hardware_connector.set(AnnetHardwareProvider())

# Set up file differ
diff.file_differ_connector.set(UnifiedFileDiffer())
```

## Device Management

### Create Device Storage

```python
from annet.storage import get_storage
from annet.cli_args import QueryOptions

# Get storage provider
storage_provider, conf_params = get_storage()

# Create storage options
storage_opts = storage_provider.opts().parse_params(conf_params, cli_args)

# Create storage instance
with storage_provider.storage()(storage_opts) as storage:
    # Query devices
    query = storage_provider.query().new(["router1", "router2"])
    devices = storage.make_devices(query)
    
    for device in devices:
        print(f"Device: {device.hostname} ({device.fqdn})")
        print(f"Hardware: {device.hw.vendor} {device.hw.model}")
        print(f"Breed: {device.breed}")
```

### Device Interface Management

```python
# Create LAG interface
lag = device.make_lag(
    lag=1,
    ports=["GigabitEthernet0/0/1", "GigabitEthernet0/0/2"],
    lag_min_links=1
)

# Add SVI interface
svi = device.add_svi(100)

# Add sub-interface
subif = device.add_subif("GigabitEthernet0/0/1", 100)

# Find existing interface
interface = device.find_interface("GigabitEthernet0/0/1")

# Add IP address to interface
interface.add_addr("192.168.1.1/24", vrf="default")
```

## Configuration Generation

### Create Custom Generator

```python
from annet.generators.base import TextGenerator
from annet.storage import Device

class BGPGenerator(TextGenerator):
    TYPE = "PARTIAL"
    TAGS = ["bgp", "routing"]
    
    def supports_device(self, device: Device) -> bool:
        return device.hw.vendor in ["cisco", "juniper"]
    
    def acl(self, device: Device) -> str:
        return """
        router bgp.*
        interface.*
        """
    
    def acl_safe(self, device: Device) -> str:
        return """
        router bgp.*
        """
    
    def __call__(self, device: Device) -> str:
        if not self.supports_device(device):
            return ""
        
        # Generate BGP configuration
        self + "router bgp 65001"
        self + " router-id 1.1.1.1"
        self + " neighbor 192.168.1.1 remote-as 65002"
        self + " neighbor 192.168.1.1 description Peer Router"
        
        return str(self)

# Use generator
generator = BGPGenerator()
config = generator(device)
print(config)
```

### Create Entire Generator

```python
from annet.generators.entire import Entire

class SystemConfigGenerator(Entire):
    TYPE = "ENTIRE"
    TAGS = ["system", "base"]
    
    def supports_device(self, device: Device) -> bool:
        return True
    
    def path(self, device: Device) -> str:
        return f"/etc/network/{device.hostname}.conf"
    
    def prio(self, device: Device) -> int:
        return 100
    
    def is_safe(self, device: Device) -> bool:
        return True
    
    def get_reload_cmds(self, device: Device) -> str:
        return "systemctl reload networking"
    
    def __call__(self, device: Device) -> str:
        config = f"""# Configuration for {device.hostname}
hostname {device.hostname}
interface eth0
  ip address 192.168.1.1/24
  description Management Interface
"""
        return config
```

### Run Generators

```python
from annet.generators import run_partial_generators, run_file_generators
from annet.types import GeneratorPartialRunArgs

# Run partial generators
run_args = GeneratorPartialRunArgs(
    device=device,
    use_acl=True,
    use_acl_safe=False,
    annotate=False
)

partial_result = run_partial_generators(
    generators=[BGPGenerator()],
    ref_generators=[],
    run_args=run_args
)

# Run file generators
file_result = run_file_generators(
    generators=[SystemConfigGenerator()],
    device=device
)
```

## Configuration Deployment

### Basic Deployment

```python
from annet.api import Deployer, deploy
from annet.deploy import get_fetcher, get_deployer
from annet.cli_args import DeployOptions

# Create deployment options
args = DeployOptions()
args.query = ["router1", "router2"]
args.no_ask_deploy = False
args.dont_commit = False
args.rollback = True

# Create deployer
deployer = Deployer(args)

# Get fetcher and deploy driver
fetcher = get_fetcher()
deploy_driver = get_deployer()

# Deploy configurations
exit_code = deploy(
    args=args,
    loader=config_loader,
    deployer=deployer,
    filterer=filterer,
    fetcher=fetcher,
    deploy_driver=deploy_driver
)
```

### Advanced Deployment with Progress

```python
import asyncio
from annet.api import adeploy
from annet.deploy_ui import ProgressBars

async def deploy_with_progress():
    # Create progress bars
    progress_bar = ProgressBars(odict([(device.fqdn, {}) for device in devices]))
    progress_bar.init()
    
    # Deploy with progress tracking
    with progress_bar:
        progress_bar.start_terminal_refresher()
        result = await deploy_driver.bulk_deploy(deploy_cmds, args, progress_bar=progress_bar)
        await progress_bar.wait_for_exit()
    
    return result

# Run deployment
result = asyncio.run(deploy_with_progress())
```

### Custom Deployer Job

```python
from annet.api import DeployerJob

class CustomDeployerJob(DeployerJob):
    def parse_result(self, res):
        device = res.device
        old = res.get_old(self.args.acl_safe)
        new = res.get_new(self.args.acl_safe)
        
        if res.err:
            self.failed_configs[device.fqdn] = res.err
            return
        
        # Custom deployment logic
        if old != new:
            self._has_diff = True
            self.diffs[device] = new
            self.cmd_lines.extend([
                f"= {device.hostname}",
                "configure terminal",
                "interface GigabitEthernet0/0/1",
                " description Updated Interface",
                "end"
            ])
```

## Configuration Diffing and Patching

### Generate Configuration Diff

```python
from annet.diff import worker
from annet.cli_args import DiffOptions

# Create diff options
args = DiffOptions()
args.query = ["router1"]
args.config = "running"
args.show_rules = True

# Generate diff
diff = worker(device_id, args, stdin, loader, filterer)

if diff:
    print("Configuration changes detected:")
    # Process diff...
```

### File-based Diff

```python
from annet.diff import file_diff_worker
from annet.cli_args import FileDiffOptions

# Create file diff options
args = FileDiffOptions()
args.old = "old.cfg"
args.new = "new.cfg"
args.hw = "cisco"

# Compare files
diff_items = list(file_diff_worker(("old.cfg", "new.cfg"), args))

for label, diff_content, is_error in diff_items:
    print(f"=== {label} ===")
    print(diff_content)
```

### Generate Patches

```python
from annet.api import patch
from annet.cli_args import ShowPatchOptions

# Create patch options
args = ShowPatchOptions()
args.query = ["router1"]
args.add_comments = True

# Generate patches
success, fail = patch(args, loader)

for device, patch_items in success.items():
    for label, patch_content, is_error in patch_items:
        print(f"=== {label} ===")
        print(patch_content)
```

### Custom File Differ

```python
from annet.diff import FileDiffer, file_differ_connector
from annet.annlib.netdev.views.hardware import HardwareView

class CustomFileDiffer(FileDiffer):
    def diff_file(self, hw: HardwareView, path: str | Path, old: str, new: str) -> list[str]:
        if path.suffix == '.json':
            return self._diff_json(old, new)
        else:
            return self._diff_text(old, new)
    
    def _diff_json(self, old: str, new: str) -> list[str]:
        import json
        try:
            old_data = json.loads(old) if old else {}
            new_data = json.loads(new) if new else {}
            # Custom JSON diff logic
            return self._generate_json_diff(old_data, new_data)
        except json.JSONDecodeError:
            return ["Error: Invalid JSON"]
    
    def _diff_text(self, old: str, new: str) -> list[str]:
        # Standard text diff
        from annet.diff import UnifiedFileDiffer
        differ = UnifiedFileDiffer()
        return differ.diff_file(None, None, old, new)

# Register custom differ
differ = CustomFileDiffer()
file_differ_connector.set(differ)
```

## Rulebook Management

### Custom Rulebook Provider

```python
from annet.rulebook import RulebookProvider, rulebook_provider_connector
from annet.annlib.netdev.views.hardware import HardwareView

class CustomRulebookProvider(RulebookProvider):
    def __init__(self, custom_rules_dir):
        self.custom_rules_dir = custom_rules_dir
        self._cache = {}
    
    def get_rulebook(self, hw: HardwareView) -> dict:
        if hw in self._cache:
            return self._cache[hw]
        
        # Load custom rules
        rulebook = self._load_custom_rules(hw)
        self._cache[hw] = rulebook
        return rulebook
    
    def get_root_modules(self):
        return ("custom.rules",)
    
    def _load_custom_rules(self, hw):
        # Load rules from custom directory
        return {
            "patching": self._load_patching_rules(hw),
            "ordering": self._load_ordering_rules(hw),
            "deploying": self._load_deploying_rules(hw)
        }

# Use custom provider
provider = CustomRulebookProvider("/path/to/custom/rules")
rulebook_provider_connector.set(provider)
```

### Rule Compilation

```python
from annet.rulebook.patching import compile_patching_text
from annet.rulebook.ordering import compile_ordering_text
from annet.rulebook.deploying import compile_deploying_text

# Define rule text
patching_text = """
%interface
  %name
    apply: interface ${name}
    order: 100
  %description
    apply: description ${description}
    order: 200
"""

ordering_text = """
interface 100
ip 200
routing 300
"""

deploying_text = """
%interface
  %name
    apply_logic: |
      def apply_logic(hw, do_commit=True, do_finalize=True, path=None):
          before = ["configure terminal"]
          after = ["write memory"] if do_commit else []
          return before, after
    dialogs:
      "Continue?": 
        text: "yes"
        send_nl: true
    timeout: 30
"""

# Compile rules
patching_rules = compile_patching_text(patching_text, "cisco")
ordering_rules = compile_ordering_text(ordering_text, "cisco")
deploying_rules = compile_deploying_text(deploying_text, "cisco")
```

### Template Rendering

```python
from annet.annlib.lib import mako_render

# Define template
template = """
interface ${interface.name}
  description ${interface.description}
  ip address ${interface.ip} ${interface.mask}
  %if interface.vlan:
  switchport access vlan ${interface.vlan}
  %endif
"""

# Device data
device_data = {
    "interface": {
        "name": "GigabitEthernet0/0/1",
        "description": "Management Interface",
        "ip": "192.168.1.1",
        "mask": "255.255.255.0",
        "vlan": 100
    }
}

# Render template
rendered = mako_render(template, hw=hardware_view, **device_data)
print(rendered)
```

## Storage Integration

### File-based Storage

```python
import json
from annet.storage import Storage, Device, StorageProvider, StorageOpts, Query

class FileStorageOpts(StorageOpts):
    def __init__(self, inventory_file: str):
        self.inventory_file = inventory_file
    
    @classmethod
    def parse_params(cls, conf_params, cli_opts):
        return cls(conf_params.get("inventory_file", "inventory.json"))

class FileQuery(Query):
    def __init__(self, query_string: str, hosts_range=None):
        self.query_string = query_string
        self.hosts_range = hosts_range
    
    @classmethod
    def new(cls, query, hosts_range=None):
        return cls(query, hosts_range)
    
    def is_empty(self):
        return not bool(self.query_string)

class FileStorage(Storage):
    def __init__(self, opts: FileStorageOpts):
        self.opts = opts
        self.inventory = self._load_inventory()
    
    def _load_inventory(self):
        with open(self.opts.inventory_file) as f:
            return json.load(f)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def resolve_object_ids_by_query(self, query):
        if query.is_empty():
            return list(self.inventory.keys())
        return [id for id, data in self.inventory.items() 
                if query.query_string in data.get("hostname", "")]
    
    def resolve_fdnds_by_query(self, query):
        device_ids = self.resolve_object_ids_by_query(query)
        return {id: self.inventory[id]["fqdn"] for id in device_ids}
    
    def resolve_all_fdnds(self):
        return [data["fqdn"] for data in self.inventory.values()]
    
    def make_devices(self, query, **kwargs):
        device_ids = self.resolve_object_ids_by_query(query)
        return [self.get_device(id) for id in device_ids]
    
    def get_device(self, obj_id, **kwargs):
        data = self.inventory[obj_id]
        return self._create_device(obj_id, data)
    
    def _create_device(self, obj_id, data):
        # Implementation to create Device object
        pass
    
    def search_connections(self, device, neighbor):
        return []
    
    def flush_perf(self):
        pass

class FileStorageProvider(StorageProvider):
    def storage(self):
        return FileStorage
    
    def opts(self):
        return FileStorageOpts
    
    def query(self):
        return FileQuery
    
    def name(self):
        return "file"
```

## Advanced Patterns

### Parallel Processing

```python
from annet.parallel import Parallel
from annet.api import gen

# Create parallel processing pool
pool = Parallel(gen.worker, args, stdin, loader, filterer)
pool.tune_args(args)

# Run with parallel processing
success, fail = pool.run(device_ids, tolerate_fails=True, strict_exit_code=False)
```

### Progress Tracking

```python
from annet.api import PoolProgressLogger

# Create progress logger
progress_logger = PoolProgressLogger(device_fqdns)

# Add to parallel pool
pool.add_callback(progress_logger)

# Run with progress tracking
results = pool.run(device_ids)
```

### Configuration Validation

```python
def validate_configuration(config, device):
    """Validate configuration before deployment"""
    errors = []
    
    # Check for required sections
    required_sections = ["interface", "routing"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")
    
    # Check for invalid values
    if "interface" in config:
        for iface in config["interface"]:
            if "ip" in iface and not is_valid_ip(iface["ip"]):
                errors.append(f"Invalid IP address: {iface['ip']}")
    
    return errors

def is_valid_ip(ip):
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
```

### Configuration Backup

```python
import shutil
from datetime import datetime

def backup_configuration(device, config):
    """Backup configuration before deployment"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/{device.hostname}/{timestamp}"
    
    os.makedirs(backup_dir, exist_ok=True)
    
    # Save current configuration
    with open(f"{backup_dir}/current.cfg", "w") as f:
        f.write(config)
    
    # Save device info
    device_info = {
        "hostname": device.hostname,
        "fqdn": device.fqdn,
        "vendor": device.hw.vendor,
        "model": device.hw.model,
        "timestamp": timestamp
    }
    
    with open(f"{backup_dir}/device_info.json", "w") as f:
        json.dump(device_info, f, indent=2)
    
    return backup_dir
```

## Error Handling

### Comprehensive Error Handling

```python
import logging
from annet import DeployCancelled, ExecError
from annet.generators.exceptions import GeneratorError, NotSupportedDevice
from annet.storage import StorageError

logger = logging.getLogger(__name__)

def safe_deploy(device, config):
    """Safely deploy configuration with comprehensive error handling"""
    try:
        # Validate configuration
        errors = validate_configuration(config, device)
        if errors:
            raise ValueError(f"Configuration validation failed: {errors}")
        
        # Backup current configuration
        backup_dir = backup_configuration(device, config)
        logger.info(f"Configuration backed up to {backup_dir}")
        
        # Deploy configuration
        result = deploy_configuration(device, config)
        
        # Verify deployment
        if not verify_deployment(device, config):
            raise RuntimeError("Deployment verification failed")
        
        logger.info(f"Configuration deployed successfully to {device.hostname}")
        return result
        
    except DeployCancelled:
        logger.info(f"Deployment cancelled for {device.hostname}")
        raise
        
    except ExecError as e:
        logger.error(f"Execution error for {device.hostname}: {e}")
        # Attempt rollback
        rollback_configuration(device, backup_dir)
        raise
        
    except GeneratorError as e:
        logger.error(f"Generator error for {device.hostname}: {e}")
        raise
        
    except NotSupportedDevice as e:
        logger.warning(f"Device not supported: {e}")
        return None
        
    except StorageError as e:
        logger.error(f"Storage error: {e}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error for {device.hostname}: {e}")
        # Attempt rollback if backup exists
        if 'backup_dir' in locals():
            rollback_configuration(device, backup_dir)
        raise
```

### Retry Logic

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1, backoff=2):
    """Decorator for retrying operations on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Operation failed after {max_retries} retries: {e}")
                        raise
                    
                    logger.warning(f"Operation failed (attempt {retries}/{max_retries}): {e}")
                    logger.info(f"Retrying in {current_delay} seconds...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=2, backoff=2)
def deploy_with_retry(device, config):
    """Deploy configuration with retry logic"""
    return deploy_configuration(device, config)
```

## Performance Optimization

### Caching

```python
from functools import lru_cache
import hashlib

class CachedGenerator:
    def __init__(self, generator):
        self.generator = generator
        self._cache = {}
    
    def __call__(self, device):
        # Create cache key
        cache_key = self._create_cache_key(device)
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Generate configuration
        config = self.generator(device)
        
        # Cache result
        self._cache[cache_key] = config
        return config
    
    def _create_cache_key(self, device):
        # Create unique cache key based on device properties
        key_data = {
            "hostname": device.hostname,
            "vendor": device.hw.vendor,
            "model": device.hw.model,
            "generator": self.generator.__class__.__name__
        }
        return hashlib.md5(str(key_data).encode()).hexdigest()

# Use cached generator
cached_bgp = CachedGenerator(BGPGenerator())
config = cached_bgp(device)
```

### Memory Management

```python
import gc
from contextlib import contextmanager

@contextmanager
def memory_efficient_processing():
    """Context manager for memory-efficient processing"""
    try:
        yield
    finally:
        # Force garbage collection
        gc.collect()

# Use in processing loop
with memory_efficient_processing():
    for device in devices:
        config = generate_configuration(device)
        process_configuration(config)
        # Large objects are automatically cleaned up
```

### Batch Processing

```python
def process_devices_in_batches(devices, batch_size=10):
    """Process devices in batches to manage memory usage"""
    for i in range(0, len(devices), batch_size):
        batch = devices[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} devices)")
        
        # Process batch
        results = []
        for device in batch:
            try:
                result = process_device(device)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {device.hostname}: {e}")
                results.append(None)
        
        # Yield results
        yield results
        
        # Clean up batch
        del batch
        gc.collect()
```

This comprehensive set of usage examples demonstrates the full power and flexibility of the Annet API system, covering everything from basic setup to advanced patterns and performance optimization.