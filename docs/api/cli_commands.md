# Annet CLI Commands Documentation

## Overview

Annet provides a comprehensive command-line interface for network configuration management. The CLI is built on top of a flexible argument parsing system and supports various operations including configuration generation, deployment, diffing, and patching.

## Command Structure

The CLI is organized into command groups and individual commands. Each command can have subcommands and supports various options for customization.

## Main Command Groups

### `show` - Display Commands

A group of commands for showing parameters, configurations, and data from devices and data sources.

#### `show current` - Show Current Device Configuration

Display the current configuration of network devices.

**Usage:**
```bash
annet show current [OPTIONS] QUERY...
```

**Parameters:**
- `QUERY`: Device query (one or more device identifiers)

**Options:**
- `--config`: Configuration source ('running', 'empty', file path, or '-')
- `--dest`: Output destination (file or directory)
- `--no-acl`: Disable ACL filtering
- `--acl-safe`: Use stricter ACL filtering
- `--filter-acl`: Additional ACL file path
- `--parallel`: Number of parallel processes
- `--tolerate-fails`: Continue on errors

**Example:**
```bash
# Show current configuration for specific devices
annet show current router1 router2

# Show configuration with custom output
annet show current --dest /tmp/configs router1

# Show configuration with ACL filtering
annet show current --acl-safe --filter-acl /path/to/acl router1
```

#### `show device-dump` - Show Device Structure Dump

Display a dump of network devices' internal structure.

**Usage:**
```bash
annet show device-dump [OPTIONS] QUERY...
```

**Parameters:**
- `QUERY`: Device query (one or more device identifiers)

**Example:**
```bash
# Show device dump for specific devices
annet show device-dump router1 router2
```

#### `show generators` - List Applicable Generators

List generators that can be applied to devices.

**Usage:**
```bash
annet show generators [OPTIONS] [QUERY...]
```

**Options:**
- `--format`: Output format ('text' or 'json')
- `--acl-safe`: Use ACL-safe filtering
- `--allowed-gens`: Comma-separated list of allowed generators
- `--excluded-gens`: Comma-separated list of excluded generators

**Example:**
```bash
# List all generators
annet show generators

# List generators for specific device
annet show generators router1

# List generators in JSON format
annet show generators --format json
```

### `gen` - Generate Configuration

Generate configuration for network devices.

**Usage:**
```bash
annet gen [OPTIONS] QUERY...
```

**Parameters:**
- `QUERY`: Device query (one or more device identifiers)

**Options:**
- `--config`: Configuration source
- `--dest`: Output destination
- `--no-acl`: Disable ACL filtering
- `--acl-safe`: Use stricter ACL filtering
- `--filter-acl`: Additional ACL file path
- `--parallel`: Number of parallel processes
- `--tolerate-fails`: Continue on errors
- `--profile`: Show performance profiling
- `--annotate`: Annotate configuration lines with sources

**Example:**
```bash
# Generate configuration for devices
annet gen router1 router2

# Generate with custom output directory
annet gen --dest /tmp/generated router1

# Generate with performance profiling
annet gen --profile router1
```

### `diff` - Generate Configuration Diff

Generate and display differences between current and generated configurations.

**Usage:**
```bash
annet diff [OPTIONS] QUERY...
```

**Parameters:**
- `QUERY`: Device query (one or more device identifiers)

**Options:**
- `--config`: Configuration source
- `--dest`: Output destination
- `--show-rules`: Show rulebook rules in diff
- `--no-collapse`: Don't collapse identical diffs
- `--no-color`: Disable colored output
- `--parallel`: Number of parallel processes

**Example:**
```bash
# Show diff for devices
annet diff router1 router2

# Show diff with rules
annet diff --show-rules router1

# Save diff to file
annet diff --dest /tmp/diffs router1
```

### `patch` - Generate Configuration Patch

Generate configuration patches for devices.

**Usage:**
```bash
annet patch [OPTIONS] QUERY...
```

**Parameters:**
- `QUERY`: Device query (one or more device identifiers)

**Options:**
- `--config`: Configuration source
- `--dest`: Output destination
- `--add-comments`: Add comments to patches
- `--parallel`: Number of parallel processes

**Example:**
```bash
# Generate patch for devices
annet patch router1 router2

# Generate patch with comments
annet patch --add-comments router1
```

### `deploy` - Deploy Configuration

Generate and deploy configuration to network devices.

**Usage:**
```bash
annet deploy [OPTIONS] QUERY...
```

**Parameters:**
- `QUERY`: Device query (one or more device identifiers)

**Options:**
- `--config`: Configuration source
- `--no-ask-deploy`: Skip deployment confirmation
- `--dont-commit`: Don't commit changes
- `--rollback`: Suggest rollback after deployment
- `--no-check-diff`: Don't check diffs after deployment
- `--entire-reload`: Reload entire configuration
- `--max-parallel`: Maximum parallel deployments
- `--parallel`: Number of parallel processes

**Example:**
```bash
# Deploy configuration to devices
annet deploy router1 router2

# Deploy without confirmation
annet deploy --no-ask-deploy router1

# Deploy with rollback option
annet deploy --rollback router1
```

### `file-diff` - File-based Diff

Generate diffs between configuration files or directories.

**Usage:**
```bash
annet file-diff [OPTIONS] OLD NEW
```

**Parameters:**
- `OLD`: Path to old configuration file or directory
- `NEW`: Path to new configuration file or directory

**Options:**
- `--hw`: Hardware vendor or model
- `--show-rules`: Show rulebook rules
- `--no-color`: Disable colored output
- `--fails-only`: Show only failed comparisons

**Example:**
```bash
# Compare two configuration files
annet file-diff old.cfg new.cfg

# Compare configuration directories
annet file-diff /old/configs /new/configs

# Compare with specific hardware type
annet file-diff --hw cisco old.cfg new.cfg
```

### `file-patch` - File-based Patch

Generate patches between configuration files or directories.

**Usage:**
```bash
annet file-patch [OPTIONS] OLD NEW
```

**Parameters:**
- `OLD`: Path to old configuration file or directory
- `NEW`: Path to new configuration file or directory

**Options:**
- `--hw`: Hardware vendor or model
- `--add-comments`: Add comments to patches
- `--no-color`: Disable colored output

**Example:**
```bash
# Generate patch between files
annet file-patch old.cfg new.cfg

# Generate patch with comments
annet file-patch --add-comments old.cfg new.cfg
```

## Context Management Commands

### `context` - Context Management

A group of commands for managing configuration contexts.

#### `context touch` - Create Context File

Create or show the context file path.

**Usage:**
```bash
annet context touch
```

**Example:**
```bash
# Create context file
annet context touch
```

#### `context set-context` - Set Active Context

Set the current active context.

**Usage:**
```bash
annet context set-context CONTEXT_NAME
```

**Parameters:**
- `CONTEXT_NAME`: Name of the context to activate

**Example:**
```bash
# Set active context
annet context set-context production
```

#### `context edit` - Edit Context File

Open the context file in an editor.

**Usage:**
```bash
annet context edit
```

**Example:**
```bash
# Edit context file
annet context edit
```

#### `context repair` - Repair Context File

Attempt to fix the context file structure.

**Usage:**
```bash
annet context repair
```

**Example:**
```bash
# Repair context file
annet context repair
```

## Global Options

### Logging Options

- `--log-level`: Set logging level (DEBUG, DEBUG2, INFO, WARN, CRITICAL)
- `--log-json`: Output logs in JSON format
- `--log-dest`: Log destination (file, directory, or stdout)
- `--log-nogroup`: Don't create date/time subdirectories

### Connection Options

- `--ask-pass`: Ask for password when connecting
- `--connect-timeout`: Connection timeout in seconds
- `--max-slots`: Maximum concurrent connections

### Output Options

- `--dest`: Output destination
- `--no-color`: Disable colored output
- `--no-label`: Hide file name labels
- `--expand-path`: Use full paths for file outputs

### Performance Options

- `--parallel`: Number of parallel processes
- `--max-tasks`: Maximum tasks per worker
- `--profile`: Show performance profiling
- `--show-hosts-progress`: Show progress per host

## Usage Examples

### Basic Configuration Generation

```bash
# Generate configuration for a single device
annet gen router1

# Generate for multiple devices
annet gen router1 router2 switch1

# Generate with custom output
annet gen --dest /tmp/configs router1
```

### Configuration Deployment

```bash
# Deploy with confirmation
annet deploy router1

# Deploy without confirmation
annet deploy --no-ask-deploy router1

# Deploy with rollback option
annet deploy --rollback router1
```

### Configuration Comparison

```bash
# Show differences
annet diff router1

# Compare files
annet file-diff old.cfg new.cfg

# Generate patches
annet patch router1
```

### Advanced Usage

```bash
# Use specific generators
annet gen --allowed-gens BGP,OSPF router1

# Use ACL filtering
annet gen --acl-safe --filter-acl /path/to/acl router1

# Parallel processing
annet gen --parallel 4 router1 router2 router3

# Performance profiling
annet gen --profile --show-hosts-progress router1
```

## Error Handling

The CLI provides comprehensive error handling:

- **Exit codes**: Different exit codes indicate different types of failures
- **Error reporting**: Detailed error messages with context
- **Tolerance**: Use `--tolerate-fails` to continue on errors
- **Logging**: Detailed logging for debugging

## Configuration Files

Annet uses several configuration files:

- **Context file**: `~/.annet/context.yml` (configurable via `ANN_CONTEXT_CONFIG_PATH`)
- **Logging config**: `configs/logging.yaml`
- **Rulebooks**: Vendor-specific rule files in `rulebook/texts/`

## Environment Variables

- `ANN_CONTEXT_CONFIG_PATH`: Path to context configuration file
- `ANN_SELECTED_CONTEXT`: Currently selected context
- `ANN_GENERATORS_CONTEXT`: Generators context override
- `ANN_CONNECT_TIMEOUT`: Default connection timeout
- `ANN_MAX_DEPLOY`: Maximum concurrent deployments