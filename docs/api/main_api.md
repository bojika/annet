# Annet Main API Documentation

## Overview

Annet is a network configuration management tool that provides a comprehensive API for generating, deploying, and managing network device configurations. The main API is exposed through the `annet` package and provides core functionality for network automation.

## Core API Functions

### `annet.init(options: Namespace)`

Initialize the Annet framework with logging and configuration.

**Parameters:**
- `options` (Namespace): Configuration options including logging level and package name

**Example:**
```python
import annet
from argparse import Namespace

options = Namespace()
options.log_level = "INFO"
options.pkg_name = "annet"
options.logging_config = "configs/logging.yaml"

annet.init(options)
```

### `annet.fill_base_args(parser: ArgParser, pkg_name: str, logging_config: str)`

Add base command-line arguments to an argument parser.

**Parameters:**
- `parser` (ArgParser): The argument parser to configure
- `pkg_name` (str): Package name for configuration
- `logging_config` (str): Path to logging configuration file

**Example:**
```python
from annet.argparse import ArgParser
import annet

parser = ArgParser()
annet.fill_base_args(parser, "annet", "configs/logging.yaml")
```

### `annet.init_logging(options: Namespace)`

Initialize logging system with the provided options.

**Parameters:**
- `options` (Namespace): Configuration options containing logging settings

**Example:**
```python
from argparse import Namespace
import annet

options = Namespace()
options.log_level = "DEBUG"
options.pkg_name = "annet"
options.logging_config = "configs/logging.yaml"

annet.init_logging(options)
```

### `annet.assert_python_version()`

Verify that the Python version meets the minimum requirements (Python 3.10.0+).

**Raises:**
- `SystemExit`: If Python version is below 3.10.0

**Example:**
```python
import annet

# This will exit with error code 1 if Python version is too old
annet.assert_python_version()
```

## Exported Exceptions

### `annet.DeployCancelled`

Exception raised when a deployment operation is cancelled.

**Example:**
```python
from annet import DeployCancelled

try:
    # Some deployment operation
    pass
except DeployCancelled:
    print("Deployment was cancelled")
```

### `annet.ExecError`

Exception raised when an execution error occurs during operations.

**Example:**
```python
from annet import ExecError

try:
    # Some execution operation
    pass
except ExecError as e:
    print(f"Execution error: {e}")
```

## Constants

### `annet.DEBUG2_LEVELV_NUM`

Numeric value for DEBUG2 logging level (value: 9).

**Example:**
```python
import annet
import logging

# Add custom DEBUG2 level
logging.addLevelName(annet.DEBUG2_LEVELV_NUM, "DEBUG2")
```

## Usage Patterns

### Basic Initialization

```python
import annet
from annet.argparse import ArgParser

# Create argument parser
parser = ArgParser()

# Add base arguments
annet.fill_base_args(parser, "annet", "configs/logging.yaml")

# Parse arguments
args = parser.parse_args()

# Initialize annet
annet.init(args)
```

### Error Handling

```python
import annet
from annet import DeployCancelled, ExecError

try:
    # Your annet operations here
    pass
except DeployCancelled:
    print("Operation was cancelled by user")
except ExecError as e:
    print(f"Execution failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Logging Configuration

```python
import annet
from argparse import Namespace

# Configure logging
options = Namespace()
options.log_level = "INFO"
options.pkg_name = "annet"
options.logging_config = "configs/logging.yaml"

annet.init_logging(options)
```

## Integration with CLI

The main API is designed to work seamlessly with the command-line interface. The `annet.py` script demonstrates the typical usage pattern:

```python
#!/usr/bin/env python3
import annet
from annet import argparse, cli, generators, hardware, lib, rulebook, diff

def main():
    annet.assert_python_version()
    parser = argparse.ArgParser()
    cli.fill_base_args(parser, annet.__name__, "configs/logging.yaml")
    
    # Set up connectors
    rulebook.rulebook_provider_connector.set(rulebook.DefaultRulebookProvider)
    hardware.hardware_connector.set(hardware.AnnetHardwareProvider)
    diff.file_differ_connector.set(diff.UnifiedFileDiffer)
    
    # Add commands and dispatch
    parser.add_commands(parser.find_subcommands(cli.list_subcommands()))
    return parser.dispatch(pre_call=annet.init, add_help_command=True)
```

## Dependencies

The main API depends on several external packages:
- `colorama`: For cross-platform colored terminal output
- `yaml`: For YAML configuration file parsing
- `contextlog`: For structured logging
- `valkit.python`: For input validation

## Thread Safety

The main API functions are designed to be thread-safe and can be used in multi-threaded applications. However, some operations like logging initialization should be performed once per application instance.