# Annet API Documentation

## Overview

Annet is a comprehensive network configuration management tool that provides a powerful API for automating network device configuration generation, deployment, and management. This documentation covers all public APIs, functions, and components with detailed examples and usage instructions.

## Table of Contents

### Core APIs

1. **[Main API](main_api.md)** - Core framework initialization and base functionality
2. **[CLI Commands](cli_commands.md)** - Command-line interface and subcommands
3. **[Generators API](generators_api.md)** - Configuration generation system
4. **[Storage API](storage_api.md)** - Device and inventory management
5. **[Deploy API](deploy_api.md)** - Configuration deployment system
6. **[Diff API](diff_api.md)** - Configuration comparison and patching
7. **[Rulebook API](rulebook_api.md)** - Rule management and template system

### Additional Resources

8. **[Usage Examples](usage_examples.md)** - Comprehensive usage examples and patterns

## Quick Start

### Installation

```bash
pip install annet
```

### Basic Usage

```python
import annet
from annet.argparse import ArgParser

# Initialize framework
annet.assert_python_version()
parser = ArgParser()
annet.fill_base_args(parser, "annet", "configs/logging.yaml")

# Parse arguments and initialize
args = parser.parse_args()
annet.init(args)
```

### Generate Configuration

```python
from annet.api import gen
from annet.cli_args import ShowGenOptions

# Create generation options
args = ShowGenOptions()
args.query = ["router1", "router2"]

# Generate configuration
success, fail = gen(args, loader)
```

### Deploy Configuration

```python
from annet.api import deploy
from annet.cli_args import DeployOptions

# Create deployment options
args = DeployOptions()
args.query = ["router1", "router2"]

# Deploy configuration
exit_code = deploy(args, loader, deployer, filterer, fetcher, deploy_driver)
```

## Architecture Overview

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Layer    │    │   API Layer     │    │  Core Layer     │
│                 │    │                 │    │                 │
│ • Commands      │◄───┤ • Generators    │◄───┤ • Storage       │
│ • Arguments     │    │ • Deploy        │    │ • Rulebook      │
│ • Output        │    │ • Diff/Patch    │    │ • Hardware      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

```
Device Query → Storage → Generators → Diff/Patch → Deploy → Results
     ↓           ↓          ↓           ↓          ↓        ↓
   Query    Device Data  Config Gen  Changes   Commands  Status
```

## Key Features

### 🔧 Configuration Generation
- **Multiple Generator Types**: Partial, Entire, and JSON Fragment generators
- **Vendor Support**: Cisco, Juniper, Huawei, and more
- **Template System**: Mako-based templating with device-specific data
- **ACL Filtering**: Access control for generated configurations

### 🚀 Deployment Management
- **Parallel Processing**: Deploy to multiple devices simultaneously
- **Progress Tracking**: Real-time deployment progress monitoring
- **Rollback Support**: Automatic rollback on deployment failure
- **Validation**: Pre and post-deployment configuration validation

### 📊 Diff and Patching
- **Unified Diffs**: Standardized diff format across vendors
- **File Comparison**: Compare configuration files and directories
- **Patch Generation**: Create executable configuration patches
- **Collapsing**: Group identical diffs for multiple devices

### 🗄️ Storage Integration
- **Multiple Backends**: File, database, and API-based storage
- **Device Management**: Comprehensive device and interface management
- **Query System**: Flexible device querying and filtering
- **Relationship Tracking**: Device connectivity and neighbor management

### 📋 Rulebook System
- **Vendor Rules**: Vendor-specific configuration rules
- **Template Rendering**: Dynamic configuration generation
- **Rule Compilation**: Compile rules for different hardware types
- **Caching**: Efficient rule caching and management

## API Design Principles

### 1. Modularity
Each API component is designed to be independent and reusable:
- **Generators**: Pluggable configuration generation
- **Storage**: Swappable data backends
- **Deployers**: Configurable deployment strategies

### 2. Extensibility
The API is designed for easy extension:
- **Custom Generators**: Create vendor-specific generators
- **Storage Providers**: Implement custom storage backends
- **Rule Definitions**: Define custom configuration rules

### 3. Error Handling
Comprehensive error handling throughout:
- **Graceful Degradation**: Handle partial failures
- **Detailed Logging**: Comprehensive logging for debugging
- **Recovery**: Automatic recovery and rollback mechanisms

### 4. Performance
Optimized for large-scale deployments:
- **Parallel Processing**: Multi-threaded operations
- **Caching**: Intelligent caching of rules and configurations
- **Memory Management**: Efficient memory usage patterns

## Common Use Cases

### 1. Configuration Management
```python
# Generate configuration for multiple devices
from annet.api import gen
from annet.cli_args import ShowGenOptions

args = ShowGenOptions()
args.query = ["router1", "router2", "switch1"]
success, fail = gen(args, loader)
```

### 2. Configuration Deployment
```python
# Deploy configuration with rollback support
from annet.api import deploy
from annet.cli_args import DeployOptions

args = DeployOptions()
args.query = ["router1", "router2"]
args.rollback = True
exit_code = deploy(args, loader, deployer, filterer, fetcher, deploy_driver)
```

### 3. Configuration Comparison
```python
# Compare current and generated configurations
from annet.api import diff
from annet.cli_args import DiffOptions

args = DiffOptions()
args.query = ["router1"]
args.show_rules = True
diffs, failed = diff(args, loader, device_ids)
```

### 4. Custom Generator Development
```python
# Create custom configuration generator
from annet.generators.base import TextGenerator

class CustomGenerator(TextGenerator):
    TYPE = "PARTIAL"
    TAGS = ["custom", "routing"]
    
    def __call__(self, device):
        # Generate custom configuration
        return "custom config"
```

## Configuration

### Context Configuration
Annet uses a context-based configuration system:

```yaml
# ~/.annet/context.yml
storage:
  provider: "file"
  params:
    inventory_file: "/path/to/inventory.json"

generators:
  default:
    - "annet.generators.bgp"
    - "annet.generators.ospf"

rulebook:
  provider: "default"
  root_dir: "/path/to/rules"
```

### Environment Variables
- `ANN_CONTEXT_CONFIG_PATH`: Path to context configuration
- `ANN_SELECTED_CONTEXT`: Currently selected context
- `ANN_GENERATORS_CONTEXT`: Generators context override
- `ANN_CONNECT_TIMEOUT`: Connection timeout
- `ANN_MAX_DEPLOY`: Maximum concurrent deployments

## Error Handling

### Exception Hierarchy
```
Exception
├── DeployCancelled
├── ExecError
├── GeneratorError
│   └── NotSupportedDevice
├── StorageError
└── RulebookError
```

### Error Handling Patterns
```python
try:
    # Annet operation
    result = annet_operation()
except DeployCancelled:
    # Handle cancellation
    pass
except ExecError as e:
    # Handle execution errors
    logger.error(f"Execution failed: {e}")
except GeneratorError as e:
    # Handle generator errors
    logger.error(f"Generation failed: {e}")
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
```

## Performance Considerations

### Parallel Processing
```python
# Use parallel processing for multiple devices
from annet.parallel import Parallel

pool = Parallel(worker_function, args, stdin, loader, filterer)
pool.tune_args(args)
results = pool.run(device_ids, tolerate_fails=True)
```

### Caching
```python
# Leverage built-in caching
from annet.rulebook import get_rulebook

# Rules are automatically cached
rulebook1 = get_rulebook(hw)  # Compiles and caches
rulebook2 = get_rulebook(hw)  # Returns cached version
```

### Memory Management
```python
# Use context managers for resource cleanup
with storage_provider.storage()(storage_opts) as storage:
    devices = storage.make_devices(query)
    # Process devices
# Storage is automatically cleaned up
```

## Best Practices

### 1. Generator Development
- **Single Responsibility**: Each generator should handle one aspect
- **Device Support**: Always implement `supports_device()`
- **ACL Rules**: Provide both `acl()` and `acl_safe()` methods
- **Error Handling**: Use appropriate exceptions

### 2. Storage Implementation
- **Connection Management**: Use context managers
- **Error Handling**: Implement proper error handling
- **Performance**: Consider caching and optimization
- **Thread Safety**: Ensure thread-safe operations

### 3. Deployment Safety
- **Testing**: Test in non-production environments
- **Backup**: Always backup before deployment
- **Rollback**: Implement rollback procedures
- **Validation**: Validate configurations before deployment

### 4. Performance
- **Parallel Processing**: Use for multiple devices
- **Caching**: Leverage built-in caching
- **Memory Management**: Clean up resources properly
- **Monitoring**: Monitor performance metrics

## Contributing

### Adding New Generators
1. Create generator class inheriting from `BaseGenerator`
2. Implement required methods (`__call__`, `supports_device`, etc.)
3. Add to generator module
4. Update context configuration

### Adding New Storage Providers
1. Implement `StorageProvider` interface
2. Create `Storage`, `StorageOpts`, and `Query` classes
3. Register with storage connector
4. Update configuration

### Adding New Rule Definitions
1. Create rule files in `rulebook/texts/`
2. Define patching, ordering, and deploying rules
3. Test with target hardware
4. Update documentation

## Support

### Documentation
- **API Reference**: This documentation
- **CLI Help**: `annet --help` and `annet <command> --help`
- **Examples**: See [Usage Examples](usage_examples.md)

### Community
- **Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Contributing**: Submit pull requests and improvements

### Getting Help
1. Check this documentation
2. Review usage examples
3. Check CLI help messages
4. Search existing issues
5. Create new issue with details

## License

This project is licensed under the terms specified in the LICENSE file.

---

For more detailed information about specific APIs, please refer to the individual documentation files linked in the table of contents above.