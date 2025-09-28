# Annet Generators API Documentation

## Overview

The Generators API is the core of Annet's configuration generation system. It provides a flexible framework for creating, managing, and executing configuration generators for network devices. Generators are responsible for producing device-specific configuration based on device properties and business logic.

## Generator Types

Annet supports three main types of generators:

1. **Partial Generators**: Generate specific parts of configuration
2. **Entire Generators**: Generate complete configuration files
3. **JSON Fragment Generators**: Generate JSON configuration fragments

## Base Classes

### `BaseGenerator`

The base class for all generators.

```python
from annet.generators.base import BaseGenerator

class MyGenerator(BaseGenerator):
    TYPE = "PARTIAL"  # or "ENTIRE" or "JSON_FRAGMENT"
    TAGS = ["my_tag", "another_tag"]
    
    def supports_device(self, device) -> bool:
        return True  # Override to add device support logic
```

**Attributes:**
- `TYPE` (str): Generator type ("PARTIAL", "ENTIRE", or "JSON_FRAGMENT")
- `TAGS` (List[str]): List of tags for categorization

**Methods:**
- `supports_device(device) -> bool`: Check if generator supports the device

### `TreeGenerator`

Base class for generators that build hierarchical configuration structures.

```python
from annet.generators.base import TreeGenerator

class MyTreeGenerator(TreeGenerator):
    def __init__(self, indent="  "):
        super().__init__(indent)
    
    def generate_config(self, device):
        with self.block("interface", "GigabitEthernet0/0/1"):
            self._append_text("description My Interface")
            with self.block("ip", "address", "192.168.1.1", "255.255.255.0"):
                pass
        return str(self)
```

**Methods:**
- `block(*tokens, indent=None)`: Create a configuration block
- `block_if(*tokens, condition=DefaultBlockIfCondition)`: Conditional block
- `multiblock(*blocks)`: Multiple nested blocks
- `multiblock_if(*blocks, condition=DefaultBlockIfCondition)`: Conditional multiblock

### `TextGenerator`

A generator that produces plain text output.

```python
from annet.generators.base import TextGenerator

class MyTextGenerator(TextGenerator):
    def __call__(self, device):
        self + "hostname " + device.hostname
        self + "interface GigabitEthernet0/0/1"
        self + " description My Interface"
        return str(self)
```

## Generator Types

### Partial Generators

Partial generators produce specific parts of device configuration. They are the most common type and are used for generating individual configuration sections.

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
        interface.*
        router bgp.*
        """
    
    def acl_safe(self, device: Device) -> str:
        return """
        router bgp.*
        """
    
    def __call__(self, device: Device) -> str:
        if not self.supports_device(device):
            return ""
        
        self + "router bgp 65001"
        self + " neighbor 192.168.1.1 remote-as 65002"
        self + " neighbor 192.168.1.1 description Peer Router"
        
        return str(self)
```

### Entire Generators

Entire generators produce complete configuration files. They are used for generating entire configuration files that replace existing ones.

```python
from annet.generators.entire import Entire
from annet.storage import Device

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

### JSON Fragment Generators

JSON fragment generators produce JSON configuration fragments for modern network devices that support JSON-based configuration.

```python
from annet.generators.jsonfragment import JSONFragment
from annet.storage import Device

class BGPJSONGenerator(JSONFragment):
    TYPE = "JSON_FRAGMENT"
    TAGS = ["bgp", "json"]
    
    def supports_device(self, device: Device) -> bool:
        return device.hw.vendor == "juniper"
    
    def path(self, device: Device) -> str:
        return "protocols/bgp"
    
    def acl(self, device: Device) -> list:
        return ["protocols.bgp"]
    
    def acl_safe(self, device: Device) -> list:
        return ["protocols.bgp"]
    
    def reload_prio(self, device: Device) -> int:
        return 50
    
    def get_reload_cmds(self, device: Device) -> str:
        return "commit"
    
    def __call__(self, device: Device) -> dict:
        return {
            "group": "external",
            "neighbor": {
                "192.168.1.1": {
                    "peer-as": 65002,
                    "description": "Peer Router"
                }
            }
        }
```

## Generator Management

### `Generators` Class

A collection class that manages different types of generators.

```python
from annet.generators import Generators, build_generators
from annet.cli_args import GenSelectOptions

# Build generators for a device
gens = build_generators(storage, gen_options, device)

# Access different generator types
partial_gens = gens.partial
entire_gens = gens.entire
json_fragment_gens = gens.json_fragment
ref_gens = gens.ref
```

### Generator Selection

Generators can be filtered and selected based on various criteria:

```python
from annet.generators import select_generators, get_list

# Get list of available generators
generator_list = get_list(show_generators_options)

# Select generators based on criteria
selected_gens = list(select_generators(gen_options, all_generators))
```

## Generator Execution

### Running Partial Generators

```python
from annet.generators import run_partial_generators, run_partial_initial
from annet.types import GeneratorPartialRunArgs

# Run initial configuration
initial_result = run_partial_initial(device)

# Run specific generators
run_args = GeneratorPartialRunArgs(
    device=device,
    use_acl=True,
    use_acl_safe=False,
    annotate=False
)

result = run_partial_generators(generators, ref_generators, run_args)
```

### Running File Generators

```python
from annet.generators import run_file_generators

# Run entire and JSON fragment generators
result = run_file_generators(file_generators, device)
```

## Generator Results

### `GeneratorPartialResult`

Result from running a partial generator.

```python
from annet.types import GeneratorPartialResult

result = GeneratorPartialResult(
    name="BGPGenerator",
    tags=["bgp", "routing"],
    acl="interface.*\nrouter bgp.*",
    acl_rules=compiled_acl_rules,
    acl_safe="router bgp.*",
    acl_safe_rules=compiled_acl_safe_rules,
    output="router bgp 65001\n...",
    config=parsed_config_tree,
    safe_config=safe_parsed_config_tree,
    perf=performance_metrics
)
```

### `GeneratorEntireResult`

Result from running an entire generator.

```python
from annet.types import GeneratorEntireResult

result = GeneratorEntireResult(
    name="SystemConfigGenerator",
    tags=["system", "base"],
    path="/etc/network/router.conf",
    output="hostname router\n...",
    reload="systemctl reload networking",
    prio=100,
    perf=performance_metrics,
    is_safe=True
)
```

### `GeneratorJSONFragmentResult`

Result from running a JSON fragment generator.

```python
from annet.types import GeneratorJSONFragmentResult

result = GeneratorJSONFragmentResult(
    name="BGPJSONGenerator",
    tags=["bgp", "json"],
    path="protocols/bgp",
    acl=["protocols.bgp"],
    acl_safe=["protocols.bgp"],
    config={"group": "external", ...},
    reload="commit",
    perf=performance_metrics,
    reload_prio=50
)
```

## Generator Performance

### `GeneratorPerf` Class

Tracks performance metrics for generators.

```python
from annet.types import GeneratorPerf

perf = GeneratorPerf(
    total=0.123,  # Total execution time
    rt=[{"name": "acl_apply", "duration": 0.045}],  # Runtime metrics
    meta={"memory_usage": "2.5MB"}  # Additional metadata
)
```

### Performance Measurement

```python
from annet.generators.perf import GeneratorPerfMesurer

with GeneratorPerfMesurer(generator, run_args=run_args) as pm:
    # Generator execution
    result = generator(device)
    
# Access performance data
performance = pm.last_result
```

## Generator Validation

### Required Packages Check

```python
from annet.generators import check_entire_generators_required_packages

# Check if required packages are installed
errors = check_entire_generators_required_packages(
    generators, 
    device_packages
)

if errors:
    for error in errors:
        print(f"Missing package: {error}")
```

### Generator Description

```python
from annet.generators import get_description

# Get generator description
description = get_description(MyGenerator)
```

## Generator Registration

### Module-based Registration

Generators are typically registered through modules that provide a `get_generators` function:

```python
# my_generators.py
from annet.generators.base import TextGenerator

class MyGenerator(TextGenerator):
    TYPE = "PARTIAL"
    TAGS = ["my_tag"]

def get_generators(storage):
    return [MyGenerator()]
```

### Context Configuration

Generators are configured through the context system:

```yaml
# context.yml
generators:
  default:
    - "my_generators"
    - "other_generators"
  
  production:
    - "my_generators"
    - "prod_specific_generators"
```

## Best Practices

### Generator Design

1. **Single Responsibility**: Each generator should handle one specific aspect of configuration
2. **Device Support**: Always implement `supports_device()` method
3. **ACL Rules**: Provide both `acl()` and `acl_safe()` methods
4. **Error Handling**: Use appropriate exception handling
5. **Performance**: Consider performance implications of complex operations

### Example: Complete Generator

```python
from annet.generators.base import TextGenerator
from annet.storage import Device
from annet.annlib.errors import NotSupportedDevice

class OSPFGenerator(TextGenerator):
    TYPE = "PARTIAL"
    TAGS = ["ospf", "routing", "igp"]
    
    def supports_device(self, device: Device) -> bool:
        return device.hw.vendor in ["cisco", "juniper", "huawei"]
    
    def acl(self, device: Device) -> str:
        return """
        router ospf.*
        interface.*
        """
    
    def acl_safe(self, device: Device) -> str:
        return """
        router ospf.*
        """
    
    def __call__(self, device: Device) -> str:
        if not self.supports_device(device):
            raise NotSupportedDevice(f"OSPF not supported on {device.hw.vendor}")
        
        # Generate OSPF configuration based on device properties
        if device.hw.vendor == "cisco":
            return self._generate_cisco_ospf(device)
        elif device.hw.vendor == "juniper":
            return self._generate_juniper_ospf(device)
        else:
            return self._generate_generic_ospf(device)
    
    def _generate_cisco_ospf(self, device: Device) -> str:
        self + "router ospf 1"
        self + " router-id 1.1.1.1"
        self + " network 192.168.0.0 0.0.255.255 area 0"
        return str(self)
    
    def _generate_juniper_ospf(self, device: Device) -> str:
        self + "protocols {"
        with self.block("ospf", "area", "0.0.0.0"):
            self + " interface all"
        self + "}"
        return str(self)
    
    def _generate_generic_ospf(self, device: Device) -> str:
        self + "ospf {"
        self + " area 0 {"
        self + "  interface all"
        self + " }"
        self + "}"
        return str(self)
```

## Error Handling

### Common Exceptions

- `GeneratorError`: General generator execution error
- `NotSupportedDevice`: Generator doesn't support the device
- `InvalidValueFromGenerator`: Invalid value returned by generator

### Exception Handling Example

```python
from annet.generators.exceptions import GeneratorError, NotSupportedDevice

try:
    result = generator(device)
except NotSupportedDevice:
    # Generator doesn't support this device type
    pass
except GeneratorError as e:
    # Handle generator-specific errors
    logger.error(f"Generator error: {e}")
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
```