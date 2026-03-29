# Annet Rulebook API Documentation

## Overview

The Rulebook API provides a comprehensive system for managing network device configuration rules, deployment procedures, and patching logic. It supports vendor-specific rule definitions, template rendering, and dynamic rule compilation.

## Core Components

### Rulebook Provider

The rulebook provider is responsible for loading and compiling rule definitions for different hardware vendors.

### Rule Compilation

The rule compilation system processes rule definitions and creates executable rule objects.

### Template Rendering

The template rendering system processes rule templates with device-specific data.

## Rulebook Provider Interface

### `RulebookProvider`

Abstract base class for rulebook providers.

```python
from annet.rulebook import RulebookProvider
from annet.annlib.netdev.views.hardware import HardwareView

class MyRulebookProvider(RulebookProvider):
    def get_rulebook(self, hw: HardwareView) -> dict:
        # Return compiled rulebook for hardware
        pass
    
    def get_root_modules(self) -> Iterable[str]:
        # Return root module paths
        pass
```

**Methods:**
- `get_rulebook(hw)`: Get compiled rulebook for hardware
- `get_root_modules()`: Get root module paths for rule discovery

### `DefaultRulebookProvider`

Default implementation of rulebook provider.

```python
from annet.rulebook import DefaultRulebookProvider

# Create default provider
provider = DefaultRulebookProvider(
    root_dir="/path/to/rules",
    root_modules=("annet.rulebook",)
)

# Get rulebook for hardware
rulebook = provider.get_rulebook(hardware_view)
```

## Rulebook Structure

### Rulebook Dictionary

A rulebook is a dictionary containing three main sections:

```python
rulebook = {
    "patching": patching_rules,      # Configuration patching rules
    "ordering": ordering_rules,      # Configuration ordering rules
    "deploying": deploying_rules     # Deployment procedure rules
}
```

### Patching Rules

Patching rules define how configuration changes are applied.

```python
# Example patching rule
patching_rule = {
    "interface": {
        "description": "Interface configuration",
        "attrs": {
            "apply": lambda hw, config: f"interface {config['name']}",
            "order": 100
        }
    }
}
```

### Ordering Rules

Ordering rules define the sequence of configuration commands.

```python
# Example ordering rule
ordering_rule = {
    "interface": 100,
    "ip": 200,
    "routing": 300
}
```

### Deploying Rules

Deploying rules define deployment procedures and command sequences.

```python
# Example deploying rule
deploying_rule = {
    "interface": {
        "description": "Interface deployment",
        "attrs": {
            "apply_logic": lambda hw, do_commit, do_finalize, path: (
                ["configure terminal"],  # before commands
                ["write memory"] if do_commit else []  # after commands
            ),
            "dialogs": {
                "Continue?": Answer("yes", send_nl=True)
            },
            "timeout": 30
        }
    }
}
```

## Rule Compilation

### Patching Rules Compilation

```python
from annet.rulebook.patching import compile_patching_text

# Compile patching rules from text
patching_rules = compile_patching_text(
    patching_text="interface {name}\n  description {description}",
    vendor="cisco"
)
```

### Ordering Rules Compilation

```python
from annet.rulebook.ordering import compile_ordering_text

# Compile ordering rules from text
ordering_rules = compile_ordering_text(
    ordering_text="interface 100\nip 200\nrouting 300",
    vendor="cisco"
)
```

### Deploying Rules Compilation

```python
from annet.rulebook.deploying import compile_deploying_text

# Compile deploying rules from text
deploying_rules = compile_deploying_text(
    deploying_text="interface {name}\n  apply: configure terminal",
    vendor="cisco"
)
```

## Template Rendering

### Mako Template Rendering

```python
from annet.annlib.lib import mako_render

# Render template with device data
rendered_text = mako_render(
    template_text="interface ${interface.name}\n  description ${interface.description}",
    hw=hardware_view,
    interface=interface_data
)
```

### Template Escaping

```python
from annet.rulebook import DefaultRulebookProvider

# Escape Mako templates
provider = DefaultRulebookProvider()
escaped_text = provider._escape_mako(template_text)
```

## Rulebook Connector

### Getting Rulebook Provider

```python
from annet.rulebook import rulebook_provider_connector, get_rulebook

# Get configured rulebook provider
provider = rulebook_provider_connector.get()

# Get rulebook for hardware
rulebook = get_rulebook(hardware_view)
```

### Setting Rulebook Provider

```python
from annet.rulebook import rulebook_provider_connector, DefaultRulebookProvider

# Set rulebook provider
provider = DefaultRulebookProvider()
rulebook_provider_connector.set(provider)
```

## Rule Processing

### Rule Matching

```python
from annet.rulebook.deploying import match_deploy_rule

# Match deployment rule
rule = match_deploy_rule(
    rules=deploying_rules,
    cmd_path=("interface", "GigabitEthernet0/0/1"),
    context={"name": "GigabitEthernet0/0/1"}
)
```

### Rule Application

```python
from annet.rulebook.deploying import make_apply_commands

# Make apply commands from rule
before, after = make_apply_commands(
    rule=rule,
    hw=hardware_view,
    do_commit=True,
    do_finalize=True,
    path="interface.cfg"
)
```

## Vendor Support

### Vendor Aliases

```python
from annet.annlib.rbparser.platform import VENDOR_ALIASES

# Get vendor alias
rul_vendor_name = VENDOR_ALIASES.get(hw.vendor, hw.vendor)
```

### Vendor-specific Rules

```python
# Cisco rules
cisco_rules = {
    "interface": {
        "apply": lambda hw, config: f"interface {config['name']}",
        "order": 100
    }
}

# Juniper rules
juniper_rules = {
    "interface": {
        "apply": lambda hw, config: f"interfaces {config['name']}",
        "order": 100
    }
}
```

## Rule Definition Files

### Rule File Structure

Rule files are typically located in `rulebook/texts/` directory:

```
rulebook/
├── texts/
│   ├── cisco.rul          # Cisco patching rules
│   ├── cisco.order        # Cisco ordering rules
│   ├── cisco.deploy       # Cisco deployment rules
│   ├── juniper.rul        # Juniper patching rules
│   ├── juniper.order      # Juniper ordering rules
│   └── juniper.deploy     # Juniper deployment rules
```

### Rule File Format

#### Patching Rules (.rul)

```
%interface
  %name
    apply: interface ${name}
    order: 100
  %description
    apply: description ${description}
    order: 200

%ip
  %address
    apply: ip address ${address} ${mask}
    order: 300
```

#### Ordering Rules (.order)

```
interface 100
ip 200
routing 300
ospf 400
bgp 500
```

#### Deployment Rules (.deploy)

```
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
```

## Rule Caching

### Rulebook Caching

```python
from annet.rulebook import DefaultRulebookProvider

# Create provider with caching
provider = DefaultRulebookProvider()

# Rules are automatically cached
rulebook1 = provider.get_rulebook(hw)  # Compiles and caches
rulebook2 = provider.get_rulebook(hw)  # Returns cached version
```

### Template Caching

```python
# Templates are cached automatically
template1 = provider._render_rul("cisco.rul", hw)  # Renders and caches
template2 = provider._render_rul("cisco.rul", hw)  # Returns cached version
```

## Error Handling

### Rule Compilation Errors

```python
from annet.rulebook.patching import compile_patching_text

try:
    rules = compile_patching_text(patching_text, vendor)
except Exception as e:
    print(f"Rule compilation failed: {e}")
    # Handle error...
```

### Template Rendering Errors

```python
from annet.annlib.lib import mako_render

try:
    rendered = mako_render(template_text, hw=hw)
except Exception as e:
    print(f"Template rendering failed: {e}")
    # Handle error...
```

### File Not Found Errors

```python
from annet.rulebook import DefaultRulebookProvider

provider = DefaultRulebookProvider()

try:
    rulebook = provider.get_rulebook(hw)
except FileNotFoundError as e:
    print(f"Rule file not found: {e}")
    # Handle error...
```

## Configuration

### Rulebook Provider Configuration

```python
from annet.rulebook import DefaultRulebookProvider

# Configure rulebook provider
provider = DefaultRulebookProvider(
    root_dir=("/path/to/rules", "/another/path"),
    root_modules=("annet.rulebook", "custom.rules")
)

# Set as default provider
rulebook_provider_connector.set(provider)
```

### Rule File Paths

```python
# Rule files are searched in order:
# 1. root_dir[0]/texts/vendor.rul
# 2. root_dir[1]/texts/vendor.rul
# 3. root_modules[0].texts.vendor.rul
# 4. root_modules[1].texts.vendor.rul
```

## Advanced Features

### Custom Rule Functions

```python
# Define custom rule functions
def custom_apply_logic(hw, do_commit=True, do_finalize=True, path=None):
    before = ["configure terminal"]
    if hw.vendor == "cisco":
        before.append("interface range")
    after = ["write memory"] if do_commit else []
    return before, after

# Use in rule definition
rule = {
    "interface": {
        "apply_logic": custom_apply_logic
    }
}
```

### Dynamic Rule Generation

```python
def generate_dynamic_rules(device_type):
    if device_type == "switch":
        return {
            "vlan": {
                "apply": lambda hw, config: f"vlan {config['id']}",
                "order": 100
            }
        }
    elif device_type == "router":
        return {
            "routing": {
                "apply": lambda hw, config: f"router {config['protocol']}",
                "order": 200
            }
        }
```

### Rule Validation

```python
def validate_rule(rule):
    required_fields = ["apply", "order"]
    for field in required_fields:
        if field not in rule:
            raise ValueError(f"Missing required field: {field}")
    return True
```

## Best Practices

### Rule Design

1. **Modularity**: Design rules to be modular and reusable
2. **Vendor Support**: Provide vendor-specific implementations
3. **Error Handling**: Include proper error handling in rules
4. **Documentation**: Document rule behavior and parameters
5. **Testing**: Test rules with various device configurations

### Template Design

1. **Clarity**: Use clear and readable template syntax
2. **Escape Special Characters**: Properly escape Mako special characters
3. **Default Values**: Provide sensible defaults for template variables
4. **Validation**: Validate template variables before rendering

### Performance

1. **Caching**: Leverage built-in caching mechanisms
2. **Lazy Loading**: Load rules only when needed
3. **Compilation**: Pre-compile frequently used rules
4. **Memory Management**: Clean up unused rule objects

## Usage Examples

### Basic Rulebook Usage

```python
from annet.rulebook import get_rulebook, rulebook_provider_connector
from annet.rulebook import DefaultRulebookProvider

# Set up rulebook provider
provider = DefaultRulebookProvider()
rulebook_provider_connector.set(provider)

# Get rulebook for hardware
rulebook = get_rulebook(hardware_view)

# Access different rule types
patching_rules = rulebook["patching"]
ordering_rules = rulebook["ordering"]
deploying_rules = rulebook["deploying"]
```

### Custom Rulebook Provider

```python
from annet.rulebook import RulebookProvider
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
        pass

# Use custom provider
provider = CustomRulebookProvider("/path/to/custom/rules")
rulebook_provider_connector.set(provider)
```

### Rule Compilation

```python
from annet.rulebook.patching import compile_patching_text
from annet.rulebook.ordering import compile_ordering_text
from annet.rulebook.deploying import compile_deploying_text

# Compile different rule types
patching_text = """
%interface
  %name
    apply: interface ${name}
    order: 100
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
          return ["configure terminal"], ["write memory"] if do_commit else []
"""

# Compile rules
patching_rules = compile_patching_text(patching_text, "cisco")
ordering_rules = compile_ordering_text(ordering_text, "cisco")
deploying_rules = compile_deploying_text(deploying_text, "cisco")
```

### Template Rendering

```python
from annet.annlib.lib import mako_render

# Render template with device data
template = """
interface ${interface.name}
  description ${interface.description}
  ip address ${interface.ip} ${interface.mask}
"""

device_data = {
    "interface": {
        "name": "GigabitEthernet0/0/1",
        "description": "Management Interface",
        "ip": "192.168.1.1",
        "mask": "255.255.255.0"
    }
}

rendered = mako_render(template, hw=hardware_view, **device_data)
print(rendered)
# Output:
# interface GigabitEthernet0/0/1
#   description Management Interface
#   ip address 192.168.1.1 255.255.255.0
```

### Rule Matching and Application

```python
from annet.rulebook.deploying import match_deploy_rule, make_apply_commands

# Match deployment rule
rule = match_deploy_rule(
    rules=deploying_rules,
    cmd_path=("interface", "GigabitEthernet0/0/1"),
    context={"name": "GigabitEthernet0/0/1"}
)

if rule:
    # Make apply commands
    before, after = make_apply_commands(
        rule=rule,
        hw=hardware_view,
        do_commit=True,
        do_finalize=True,
        path="interface.cfg"
    )
    
    print("Before commands:", before)
    print("After commands:", after)
```