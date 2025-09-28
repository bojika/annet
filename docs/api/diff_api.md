# Annet Diff and Patching API Documentation

## Overview

The Diff and Patching API provides comprehensive functionality for comparing network device configurations, generating diffs, and creating patches. It supports both CLI-based devices and file-based configurations, with advanced features like diff collapsing, colorization, and rulebook integration.

## Core Components

### Diff Generation

The diff generation system compares old and new configurations to identify changes.

### Patching System

The patching system creates executable patches from configuration differences.

### File Differ

The file differ handles comparison of configuration files and directories.

## Diff Types

### `Diff`

Standard diff type for CLI-based device configurations.

```python
from annet.types import Diff

# Diff is a list of tuples representing configuration changes
diff: Diff = [
    (operation, path, old_value, new_value, metadata),
    # ...
]
```

### `PCDiff`

Diff type for PC-based (file-based) configurations.

```python
from annet.types import PCDiff, PCDiffFile

# PCDiff contains multiple PCDiffFile objects
pc_diff = PCDiff(
    hostname="router1",
    diff_files=[
        PCDiffFile(
            label="router1/interface.cfg",
            diff_lines=["-old line", "+new line", " context line"]
        )
    ]
)
```

## Diff Generation Functions

### `worker()`

Main worker function for generating diffs.

```python
from annet.diff import worker
from annet.cli_args import DiffOptions
from annet.gen import Loader

# Generate diff for a device
diff = worker(
    device_id=device_id,
    args=diff_options,
    stdin=stdin_data,
    loader=config_loader,
    filterer=filterer
)
```

### `pc_diff()`

Generate diff for PC-based configurations.

```python
from annet.diff import pc_diff

# Generate PC diff
pc_diff_files = list(pc_diff(
    hw=hardware_view,
    hostname="router1",
    old_files={"interface.cfg": "old content"},
    new_files={"interface.cfg": ("new content", "reload_cmd")}
))
```

### `json_fragment_diff()`

Generate diff for JSON fragment configurations.

```python
from annet.diff import json_fragment_diff

# Generate JSON fragment diff
json_diff_files = list(json_fragment_diff(
    hw=hardware_view,
    hostname="router1",
    old_files={"bgp.json": {"group": "old"}},
    new_files={"bgp.json": ({"group": "new"}, "commit")}
))
```

## Diff Processing

### `gen_sort_diff()`

Generate sorted diff output compatible with write_output.

```python
from annet.diff import gen_sort_diff
from annet.cli_args import ShowDiffOptions

# Generate sorted diff
diff_items = gen_sort_diff(diffs, show_diff_options)

for label, diff_content, is_error in diff_items:
    print(f"=== {label} ===")
    print(diff_content)
```

### `collapse_diffs()`

Collapse identical diffs for device groups.

```python
from annet.diff import collapse_diffs

# Collapse diffs by similarity
collapsed_diffs = collapse_diffs(device_diffs)

for devices, diff_obj in collapsed_diffs.items():
    device_names = [dev.hostname for dev in devices]
    print(f"Identical diff for: {', '.join(device_names)}")
```

## File Differ Interface

### `FileDiffer`

Abstract base class for file differ implementations.

```python
from annet.diff import FileDiffer
from annet.annlib.netdev.views.hardware import HardwareView
from pathlib import Path

class MyFileDiffer(FileDiffer):
    def diff_file(self, hw: HardwareView, path: str | Path, old: str, new: str) -> list[str]:
        # Calculate differences for a file
        # Return list of diff lines
        pass
```

### `UnifiedFileDiffer`

Standard unified diff implementation.

```python
from annet.diff import UnifiedFileDiffer

# Create unified file differ
differ = UnifiedFileDiffer()
differ.context = 3  # Number of context lines

# Calculate diff
diff_lines = differ.diff_file(hw, "config.cfg", old_content, new_content)
```

### `FrrFileDiffer`

Specialized differ for FRR configuration files.

```python
from annet.diff import FrrFileDiffer

# Create FRR file differ
differ = FrrFileDiffer()

# Calculate FRR diff
diff_lines = differ.diff_file(hw, "/etc/frr/frr.conf", old_frr_config, new_frr_config)
```

## File Differ Connector

### Getting File Differ

```python
from annet.diff import file_differ_connector

# Get configured file differ
differ = file_differ_connector.get()

# Use differ
diff_lines = differ.diff_file(hw, "config.cfg", old_content, new_content)
```

## Diff Formatting

### Colorization

```python
from annet.annlib.diff import colorize_line, format_file_diff

# Colorize diff lines
colored_lines = [colorize_line(line) for line in diff_lines]

# Format file diff
formatted_diff = format_file_diff(diff_lines)
```

### Text Transformation

```python
from annet.diff import _transform_text_diff_for_collapsing

# Transform text diff for collapsing
transformed_diff = _transform_text_diff_for_collapsing(diff_lines)
```

## Patching System

### Patch Generation

```python
from annet import patching

# Generate patch from diff
patch_tree = patching.make_patch(
    pre=pre_config,
    rb=rulebook,
    hw=hardware_view,
    add_comments=True,
    orderer=orderer,
    do_commit=True
)
```

### Patch Application

```python
from annet import patching

# Apply patch to configuration
patched_config = patching.apply_patch(
    config=original_config,
    patch=patch_tree,
    hw=hardware_view
)
```

### Ordering

```python
from annet import patching

# Create orderer
orderer = patching.Orderer(ordering_rules, hw.vendor)

# Order configuration
ordered_config = orderer.order_config(config)

# Insert references
orderer.ref_insert(ref_tracker)
```

## Rulebook Integration

### Diff Rules

```python
from annet import patching, rulebook

# Get rulebook
rb = rulebook.get_rulebook(hw)

# Make diff with rules
diff_tree = patching.make_diff(
    old_config,
    new_config,
    rb,
    [acl_rules, filter_acl_rules]
)

# Strip unchanged parts
diff_tree = patching.strip_unchanged(diff_tree)
```

### ACL Integration

```python
from annet import patching

# Apply ACL rules
filtered_config = patching.apply_acl(
    config=config,
    rules=acl_rules,
    fatal_acl=True,
    with_annotations=True
)
```

## File Operations

### File Diff Worker

```python
from annet.diff import file_diff_worker

# Process file diff
diff_items = list(file_diff_worker(
    old_new=("old.cfg", "new.cfg"),
    args=file_diff_options
))

for label, diff_content, is_error in diff_items:
    print(f"=== {label} ===")
    print(diff_content)
```

### File Patch Worker

```python
from annet.diff import file_patch_worker

# Process file patch
patch_items = list(file_patch_worker(
    old_new=("old.cfg", "new.cfg"),
    args=file_patch_options
))

for label, patch_content, is_error in patch_items:
    print(f"=== {label} ===")
    print(patch_content)
```

## Configuration Reading

### Old/New Config Reading

```python
from annet.api import _read_old_new_configs, _read_old_new_hw

# Read configuration files
old_config, new_config = _read_old_new_configs(old_path, new_path)

# Parse hardware and configurations
old, new, hw = _read_old_new_hw(
    old_path, old_config, 
    new_path, new_config, 
    file_input_options
)
```

### Hardware Detection

```python
from annet.api import guess_hw

# Guess hardware from configuration
hw, score = guess_hw(config_text)
```

## Diff Display

### Pre-formatting

```python
from annet.api import _print_pre_as_diff

# Print pre-formatted diff
_print_pre_as_diff(
    pre=pre_config,
    show_rules=True,
    indent="  ",
    file=output_file
)
```

### Formatter Integration

```python
from annet.vendors import registry_connector

# Get formatter for hardware
formatter = registry_connector.get().match(hw).make_formatter()

# Format diff
diff_lines = formatter.diff(diff_tree)
```

## Advanced Features

### Diff Collapsing

```python
from annet.diff import collapse_diffs

# Collapse similar diffs
collapsed = collapse_diffs(device_diffs)

# Process collapsed diffs
for devices, diff_obj in collapsed.items():
    device_names = [dev.hostname for dev in devices]
    print(f"Same diff for: {', '.join(device_names)}")
    # Process diff_obj...
```

### Performance Optimization

```python
from annet.diff import _transform_text_diff_for_collapsing

# Optimize diff for collapsing
optimized_diff = _transform_text_diff_for_collapsing(diff_lines)
```

## Error Handling

### Diff Errors

```python
from annet.diff import worker

try:
    diff = worker(device_id, args, stdin, loader, filterer)
except Exception as e:
    print(f"Diff generation failed: {e}")
    # Handle error...
```

### File Differ Errors

```python
from annet.diff import UnifiedFileDiffer

differ = UnifiedFileDiffer()

try:
    diff_lines = differ.diff_file(hw, path, old, new)
except Exception as e:
    print(f"File diff failed: {e}")
    # Handle error...
```

## Configuration

### Diff Options

```python
from annet.cli_args import ShowDiffOptions, FileDiffOptions

# CLI diff options
diff_options = ShowDiffOptions()
diff_options.show_rules = True
diff_options.no_collapse = False
diff_options.no_color = False

# File diff options
file_diff_options = FileDiffOptions()
file_diff_options.hw = "cisco"
file_diff_options.show_rules = True
```

### File Differ Configuration

```python
from annet.diff import file_differ_connector, UnifiedFileDiffer

# Configure file differ
differ = UnifiedFileDiffer()
differ.context = 5  # More context lines

# Set as default
file_differ_connector.set(differ)
```

## Best Practices

### Diff Generation

1. **Efficient Processing**: Use appropriate diff algorithms for large configurations
2. **Memory Management**: Handle large diffs efficiently
3. **Error Handling**: Provide meaningful error messages
4. **Performance**: Consider parallel processing for multiple devices

### File Differ Implementation

1. **Vendor Support**: Implement vendor-specific diff logic when needed
2. **Context Lines**: Provide appropriate context for readability
3. **Special Cases**: Handle special file types (binary, structured data)
4. **Performance**: Optimize for large files

### Patch Generation

1. **Safety**: Validate patches before application
2. **Rollback**: Ensure rollback capability
3. **Testing**: Test patches in non-production environments
4. **Documentation**: Document patch generation logic

## Usage Examples

### Basic Diff Generation

```python
from annet.diff import worker
from annet.cli_args import DiffOptions

# Create diff options
args = DiffOptions()
args.query = ["router1"]
args.config = "running"

# Generate diff
diff = worker(device_id, args, stdin, loader, filterer)

if diff:
    print("Configuration changes detected")
    # Process diff...
```

### File Comparison

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

### Advanced Diff Processing

```python
from annet.diff import gen_sort_diff, collapse_diffs
from annet.cli_args import ShowDiffOptions

# Generate sorted diff
args = ShowDiffOptions()
args.show_rules = True
args.no_collapse = False

diff_items = gen_sort_diff(device_diffs, args)

# Collapse similar diffs
collapsed = collapse_diffs(device_diffs)

# Process results
for devices, diff_obj in collapsed.items():
    device_names = [dev.hostname for dev in devices]
    print(f"Identical changes for: {', '.join(device_names)}")
```

### Custom File Differ

```python
from annet.diff import FileDiffer, file_differ_connector
from annet.annlib.netdev.views.hardware import HardwareView

class CustomFileDiffer(FileDiffer):
    def diff_file(self, hw: HardwareView, path: str | Path, old: str, new: str) -> list[str]:
        # Custom diff logic
        if path.suffix == '.json':
            return self._diff_json(old, new)
        else:
            return self._diff_text(old, new)
    
    def _diff_json(self, old: str, new: str) -> list[str]:
        # JSON-specific diff logic
        pass
    
    def _diff_text(self, old: str, new: str) -> list[str]:
        # Text diff logic
        pass

# Register custom differ
differ = CustomFileDiffer()
file_differ_connector.set(differ)
```