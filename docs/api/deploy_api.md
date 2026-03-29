# Annet Deployment API Documentation

## Overview

The Deployment API provides comprehensive functionality for deploying network device configurations. It includes components for fetching current configurations, applying changes, managing deployment progress, and handling rollback operations.

## Core Components

### Fetcher

The Fetcher is responsible for retrieving current configurations from network devices.

### DeployDriver

The DeployDriver handles the actual deployment of configurations to devices.

### Deployer

The Deployer orchestrates the deployment process, including diff generation, user confirmation, and progress tracking.

## Fetcher Interface

### `Fetcher`

Abstract base class for configuration fetchers.

```python
from annet.deploy import Fetcher
from annet.storage import Device

class MyFetcher(Fetcher):
    async def fetch_packages(self, devices: list[Device], processes: int = 1, max_slots: int = 0):
        # Fetch package information from devices
        packages = {}
        errors = {}
        # Implementation...
        return packages, errors
    
    async def fetch(self, devices: list[Device], files_to_download: dict[str, list[str]] = None, 
                   processes: int = 1, max_slots: int = 0):
        # Fetch configurations from devices
        # Implementation...
        pass
```

**Methods:**
- `fetch_packages()`: Fetch package information from devices
- `fetch()`: Fetch configurations from devices

### Getting Fetcher

```python
from annet.deploy import get_fetcher

# Get configured fetcher
fetcher = get_fetcher()

# Fetch configurations
await fetcher.fetch(devices, processes=4, max_slots=10)
```

## DeployDriver Interface

### `DeployDriver`

Abstract base class for deployment drivers.

```python
from annet.deploy import DeployDriver, DeployResult, ProgressBar
from annet.annlib.netdev.views.hardware import HardwareView
from annet.cli_args import DeployOptions

class MyDeployDriver(DeployDriver):
    async def bulk_deploy(self, deploy_cmds: dict, args: DeployOptions, 
                         progress_bar: ProgressBar = None) -> DeployResult:
        # Deploy configurations to multiple devices
        # Implementation...
        return DeployResult(hostnames=[], results={}, durations={}, original_states={})
    
    def apply_deploy_rulebook(self, hw: HardwareView, cmd_paths, do_finalize=True, do_commit=True):
        # Apply deployment rulebook to commands
        # Implementation...
        pass
    
    def build_configuration_cmdlist(self, hw: HardwareView, do_finalize=True, do_commit=True):
        # Build configuration command list
        # Implementation...
        pass
    
    def build_exit_cmdlist(self, hw):
        # Build exit command list
        # Implementation...
        pass
```

**Methods:**
- `bulk_deploy()`: Deploy configurations to multiple devices
- `apply_deploy_rulebook()`: Apply deployment rules to commands
- `build_configuration_cmdlist()`: Build configuration commands
- `build_exit_cmdlist()`: Build exit commands

### Getting DeployDriver

```python
from annet.deploy import get_deployer

# Get configured deployer
deployer = get_deployer()

# Deploy configurations
result = await deployer.bulk_deploy(deploy_cmds, args)
```

## Progress Tracking

### `ProgressBar` Interface

Abstract interface for deployment progress tracking.

```python
from annet.deploy import ProgressBar

class MyProgressBar(ProgressBar):
    def set_content(self, tile_name: str, content: str):
        # Set content for a progress tile
        pass
    
    def add_content(self, tile_name: str, content: str):
        # Add content to a progress tile
        pass
    
    def reset_content(self, tile_name: str):
        # Reset content for a progress tile
        pass
    
    def set_progress(self, tile_name: str, iteration: int, total: int, 
                    prefix: str = "", suffix: str = "", fill: str = "", error: bool = False):
        # Set progress for a tile
        pass
    
    def set_exception(self, tile_name: str, cmd_exc: str, last_cmd: str, 
                     progress_max: int, content: str = ""):
        # Set exception information for a tile
        pass
```

## Deployment Results

### `DeployResult`

Named tuple containing deployment results.

```python
from annet.deploy import DeployResult

# Create deployment result
result = DeployResult(
    hostnames=["router1", "router2"],
    results={"router1": None, "router2": Exception("Connection failed")},
    durations={"router1": 5.2, "router2": 0.0},
    original_states={"router1": "backup_config", "router2": None}
)

# Add results
result.add_results({"router3": Exception("Timeout")})
```

**Attributes:**
- `hostnames`: List of device hostnames
- `results`: Dictionary mapping hostnames to results (None for success, Exception for failure)
- `durations`: Dictionary mapping hostnames to deployment durations
- `original_states`: Dictionary mapping hostnames to original configuration states

## Deployer Class

### `Deployer`

Main orchestrator for deployment operations.

```python
from annet.api import Deployer
from annet.cli_args import DeployOptions

class Deployer:
    def __init__(self, args: DeployOptions):
        self.args = args
        self.cmd_lines = []
        self.deploy_cmds = OrderedDict()
        self.diffs = {}
        self.failed_configs = {}
        self.fqdn_to_device = {}
        self.empty_diff_hostnames = set()
    
    def parse_result(self, job: DeployerJob, result: OldNewResult):
        # Parse generator result and prepare for deployment
        pass
    
    def diff_lines(self) -> List[str]:
        # Generate diff lines for display
        pass
    
    def ask_deploy(self) -> str:
        # Ask user for deployment confirmation
        pass
    
    def ask_rollback(self) -> str:
        # Ask user for rollback confirmation
        pass
    
    def check_diff(self, result: DeployResult, loader: Loader):
        # Check diffs after deployment
        pass
```

## Deployment Jobs

### `DeployerJob`

Abstract base class for deployment jobs.

```python
from annet.api import DeployerJob
from annet.storage import Device
from annet.cli_args import DeployOptions

class MyDeployerJob(DeployerJob):
    def __init__(self, device: Device, args: DeployOptions):
        super().__init__(device, args)
        self.add_comments = False
        self.diff_lines = []
        self.cmd_lines = []
        self.deploy_cmds = OrderedDict()
        self.diffs = {}
        self.failed_configs = {}
        self._has_diff = False
    
    def parse_result(self, res):
        # Parse generator result
        pass
    
    def collapseable_diffs(self):
        # Return diffs that can be collapsed
        return {}
    
    def has_diff(self):
        # Check if job has differences
        return self._has_diff
```

### `CliDeployerJob`

Deployment job for CLI-based devices.

```python
from annet.api import CliDeployerJob

class MyCliDeployerJob(CliDeployerJob):
    def parse_result(self, res: OldNewResult):
        # Parse result for CLI device
        device = res.device
        old = res.get_old(self.args.acl_safe)
        new = res.get_new(self.args.acl_safe)
        acl_rules = res.get_acl_rules(self.args.acl_safe)
        
        if res.err:
            self.failed_configs[device.fqdn] = res.err
            return
        
        # Generate diff and patch
        diff_obj, patch_tree = _diff_and_patch(
            device, old, new, acl_rules, res.filter_acl_rules, 
            self.add_comments, do_commit=not self.args.dont_commit
        )
        
        if not patch_tree:
            return
        
        # Generate commands
        formatter = registry_connector.get().match(device.hw).make_formatter(indent="")
        cmds = formatter.cmd_paths(patch_tree)
        
        self._has_diff = True
        self.diffs[device] = diff_obj
        self.cmd_lines.extend(["= %s " % device.hostname, ""])
        self.cmd_lines.extend(map(itemgetter(-1), cmds))
        self.cmd_lines.append("")
        
        # Apply deployment rulebook
        deployer_driver = get_deployer()
        self.deploy_cmds[device] = deployer_driver.apply_deploy_rulebook(
            device.hw, cmds, do_commit=not self.args.dont_commit
        )
```

### `PCDeployerJob`

Deployment job for PC-based devices (file-based configuration).

```python
from annet.api import PCDeployerJob

class MyPCDeployerJob(PCDeployerJob):
    def parse_result(self, res: OldNewResult):
        # Parse result for PC device
        device = res.device
        old_files = res.old_files
        new_files = res.get_new_files(self.args.acl_safe)
        old_json_fragment_files = res.old_json_fragment_files
        new_json_fragment_files = res.get_new_file_fragments(self.args.acl_safe)
        
        if res.err:
            self.failed_configs[device.fqdn] = res.err
            return
        
        if not new_files and not new_json_fragment_files:
            return
        
        # Process files for deployment
        upload_files = {}
        reload_cmds = {}
        generator_types = {}
        
        # Handle entire files
        for file, (file_content, cmds) in new_files.items():
            if old_files.get(file) != file_content:
                self._has_diff = True
                upload_files[file] = file_content.encode()
                generator_types[file] = GeneratorType.ENTIRE
                self.cmd_lines.append("= %s/%s " % (device.hostname, file))
                self.cmd_lines.extend([file_content, ""])
                
                if self.args.entire_reload:
                    reload_cmds[file] = cmds.encode()
        
        # Handle JSON fragment files
        for file, (json_cfg, cmds) in new_json_fragment_files.items():
            old_json_cfg = old_json_fragment_files[file]
            json_patch = jsontools.make_patch(old_json_cfg, json_cfg)
            file_content = jsontools.format_json(json_patch)
            
            self._has_diff = True
            upload_files[file] = file_content.encode()
            generator_types[file] = GeneratorType.JSON_FRAGMENT
            reload_cmds[file] = cmds.encode()
        
        if self._has_diff:
            self.deploy_cmds[device] = {
                "files": upload_files,
                "cmds": reload_cmds,
                "generator_types": generator_types,
            }
```

## Deployment Process

### Main Deployment Function

```python
from annet.api import deploy

# Deploy configurations
exit_code = deploy(
    args=deploy_options,
    loader=config_loader,
    deployer=deployer,
    filterer=filterer,
    fetcher=fetcher,
    deploy_driver=deploy_driver
)
```

### Async Deployment Function

```python
from annet.api import adeploy

# Async deployment
exit_code = await adeploy(
    args=deploy_options,
    loader=config_loader,
    deployer=deployer,
    filterer=filterer,
    fetcher=fetcher,
    deploy_driver=deploy_driver
)
```

## Rulebook Integration

### Question Handling

```python
from annet.deploy import RulebookQuestionHandler, rb_question_to_question
from annet.annlib.command import Command, Question

# Create question handler
dialogs = {
    matcher1: answer1,
    matcher2: answer2
}
handler = RulebookQuestionHandler(dialogs)

# Handle device questions
def handle_question(dev, cmd: Command, match_content: bytes):
    content = match_content.strip().decode()
    for matcher, answer in handler._dialogs.items():
        if matcher(content):
            return Command(answer.text)
    return None
```

### Command Parameters

```python
from annet.deploy import make_cmd_params, fill_cmd_params

# Make command parameters from rule
cmd_params = make_cmd_params(rule)

# Fill command with parameters
fill_cmd_params(rules, cmd)
```

### Apply Commands

```python
from annet.deploy import make_apply_commands, apply_deploy_rulebook

# Make apply commands
before, after = make_apply_commands(rule, hw, do_commit=True, do_finalize=True)

# Apply deployment rulebook
cmdlist = apply_deploy_rulebook(hw, cmd_paths, do_finalize=True, do_commit=True)
```

## Progress Tracking

### Progress Logger

```python
from annet.api import PoolProgressLogger

# Create progress logger
progress_logger = PoolProgressLogger(device_fqdns)

# Use with parallel operations
pool.add_callback(progress_logger)
```

### Progress Bar Integration

```python
from annet.deploy_ui import ProgressBars

# Create progress bars
progress_bar = ProgressBars(odict([(device.fqdn, {}) for device in deploy_cmds]))
progress_bar.init()

# Use during deployment
with progress_bar:
    progress_bar.start_terminal_refresher()
    result = await deploy_driver.bulk_deploy(deploy_cmds, args, progress_bar=progress_bar)
    await progress_bar.wait_for_exit()
```

## Error Handling

### Deployment Errors

```python
from annet.api import Deployer

deployer = Deployer(args)

try:
    # Deployment operations
    pass
except Exception as e:
    # Handle deployment errors
    deployer.failed_configs[device.fqdn] = e
```

### Result Processing

```python
from annet.deploy import DeployResult

result = DeployResult(hostnames=[], results={}, durations={}, original_states={})

# Process results
for hostname, host_result in result.results.items():
    if isinstance(host_result, Exception):
        print(f"Deployment failed for {hostname}: {host_result}")
    else:
        print(f"Deployment successful for {hostname}")
```

## Configuration

### Deployer Configuration

```python
from annet.cli_args import DeployOptions

# Create deployment options
deploy_options = DeployOptions()
deploy_options.query = ["router1", "router2"]
deploy_options.no_ask_deploy = False
deploy_options.dont_commit = False
deploy_options.rollback = True
deploy_options.parallel = 4
```

### Fetcher Configuration

```python
# Fetcher is configured through connectors
from annet.deploy import get_fetcher

fetcher = get_fetcher()
```

## Best Practices

### Deployment Safety

1. **Always Test**: Test configurations in non-production environments first
2. **Backup**: Always backup current configurations before deployment
3. **Rollback**: Implement rollback procedures for failed deployments
4. **Validation**: Validate configurations before deployment
5. **Monitoring**: Monitor deployment progress and results

### Error Handling

1. **Graceful Degradation**: Handle partial failures gracefully
2. **Detailed Logging**: Log detailed information for debugging
3. **User Feedback**: Provide clear feedback to users
4. **Recovery**: Implement recovery procedures for failed deployments

### Performance

1. **Parallel Processing**: Use parallel processing for multiple devices
2. **Connection Pooling**: Reuse connections when possible
3. **Progress Tracking**: Provide progress feedback for long operations
4. **Resource Management**: Properly manage resources and connections

## Usage Examples

### Basic Deployment

```python
from annet.api import Deployer, deploy
from annet.deploy import get_fetcher, get_deployer
from annet.cli_args import DeployOptions

# Create deployment options
args = DeployOptions()
args.query = ["router1", "router2"]

# Create deployer
deployer = Deployer(args)

# Get fetcher and deploy driver
fetcher = get_fetcher()
deploy_driver = get_deployer()

# Deploy configurations
exit_code = deploy(args, loader, deployer, filterer, fetcher, deploy_driver)
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

### Rollback Deployment

```python
from annet.api import Deployer

deployer = Deployer(args)

# Check if rollback is needed
if rollback_cmds:
    ans = deployer.ask_rollback()
    if ans == "y":
        await deploy_driver.bulk_deploy(rollback_cmds, args)
```