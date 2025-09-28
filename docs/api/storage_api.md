# Annet Storage API Documentation

## Overview

The Storage API provides a unified interface for managing network devices and their data. It abstracts different data sources (databases, files, APIs) into a consistent interface that allows Annet to work with various inventory systems and data formats.

## Core Concepts

### Storage Provider

A storage provider is responsible for creating storage instances and managing connections to data sources.

### Storage Instance

A storage instance provides the actual data access methods for querying and retrieving device information.

### Device

A device represents a network device with its properties, interfaces, and relationships.

### Query

A query object represents a search criteria for finding devices.

## Storage Provider Interface

### `StorageProvider`

Abstract base class for storage providers.

```python
from annet.storage import StorageProvider

class MyStorageProvider(StorageProvider):
    def storage(self) -> Type["Storage"]:
        return MyStorage
    
    def opts(self) -> Type["StorageOpts"]:
        return MyStorageOpts
    
    def query(self) -> Type["Query"]:
        return MyQuery
    
    def name(self) -> str:
        return "my_storage"
```

**Methods:**
- `storage()`: Return the storage class
- `opts()`: Return the storage options class
- `query()`: Return the query class
- `name()`: Return provider name

## Storage Interface

### `Storage`

Abstract base class for storage implementations.

```python
from annet.storage import Storage, Device

class MyStorage(Storage):
    def __enter__(self):
        # Initialize connection
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup connection
        pass
    
    def resolve_object_ids_by_query(self, query):
        # Return list of object IDs matching query
        pass
    
    def resolve_fdnds_by_query(self, query):
        # Return mapping of object ID to FQDN
        pass
    
    def resolve_all_fdnds(self) -> list[str]:
        # Return all FQDNs
        pass
    
    def search_connections(self, device: Device, neighbor: Device):
        # Return list of interface pairs connecting devices
        pass
    
    def make_devices(self, query, preload_neighbors=False, use_mesh=None, preload_extra_fields=False, **kwargs):
        # Return list of Device objects
        pass
    
    def get_device(self, obj_id, preload_neighbors=False, use_mesh=None, **kwargs) -> Device:
        # Return single Device object
        pass
    
    def flush_perf(self):
        # Flush performance metrics
        pass
```

## Device Interface

### `Device`

Protocol defining the interface for network devices.

```python
from annet.storage import Device, Interface
from annet.annlib.netdev.views.hardware import HardwareView

class MyDevice(Device):
    def __init__(self, device_id, hostname, fqdn, hw, storage):
        self._id = device_id
        self._hostname = hostname
        self._fqdn = fqdn
        self._hw = hw
        self._storage = storage
    
    @property
    def storage(self) -> Storage:
        return self._storage
    
    def __hash__(self):
        return hash(self._id)
    
    def is_pc(self) -> bool:
        return self._hw.vendor == "pc"
    
    @property
    def hw(self) -> HardwareView:
        return self._hw
    
    @property
    def id(self):
        return self._id
    
    @property
    def fqdn(self) -> str:
        return self._fqdn
    
    @property
    def hostname(self) -> str:
        return self._hostname
    
    @property
    def neighbours_ids(self):
        # Return list of neighbor device IDs
        pass
    
    @property
    def neighbours_fqdns(self):
        # Return list of neighbor FQDNs
        pass
    
    @property
    def breed(self) -> str:
        # Return device breed/type
        pass
    
    def make_lag(self, lag: int, ports: Sequence[str], lag_min_links: Optional[int]) -> Interface:
        # Create or return LAG interface
        pass
    
    def add_svi(self, svi: int) -> Interface:
        # Add SVI interface or return existing one
        pass
    
    def add_subif(self, interface: str, subif: int) -> Interface:
        # Add sub interface or return existing one
        pass
    
    def find_interface(self, name: str) -> Optional[Interface]:
        # Find interface by name
        pass
```

## Interface Interface

### `Interface`

Protocol defining the interface for network interfaces.

```python
from annet.storage import Interface

class MyInterface(Interface):
    def __init__(self, name: str):
        self._name = name
        self._addresses = []
    
    @property
    def name(self) -> str:
        return self._name
    
    def add_addr(self, address_mask: str, vrf: Optional[str]) -> None:
        # Add IP address to interface
        self._addresses.append((address_mask, vrf))
```

## Query Interface

### `Query`

Abstract base class for device queries.

```python
from annet.storage import Query

class MyQuery(Query):
    def __init__(self, query_string: str, hosts_range: Optional[slice] = None):
        self.query_string = query_string
        self.hosts_range = hosts_range
    
    def is_empty(self) -> bool:
        return not bool(self.query_string)
    
    @classmethod
    def new(cls, query: Union[str, Iterable[str]], hosts_range: Optional[slice] = None) -> "Query":
        if isinstance(query, str):
            return cls(query, hosts_range)
        else:
            # Handle multiple query strings
            return cls(" ".join(query), hosts_range)
```

## Storage Options

### `StorageOpts`

Abstract base class for storage configuration options.

```python
from annet.storage import StorageOpts

class MyStorageOpts(StorageOpts):
    def __init__(self, host: str, port: int, database: str, **kwargs):
        self.host = host
        self.port = port
        self.database = database
        self.kwargs = kwargs
    
    @classmethod
    def parse_params(cls, conf_params: Optional[Dict[str, str]], cli_opts: Any):
        # Parse configuration parameters and CLI options
        return cls(
            host=conf_params.get("host", "localhost"),
            port=int(conf_params.get("port", "5432")),
            database=conf_params.get("database", "network_inventory"),
            **conf_params
        )
```

## Storage Connector

### Getting Storage Provider

```python
from annet.storage import get_storage

# Get storage provider and configuration
storage_provider, conf_params = get_storage()

# Create storage options
storage_opts = storage_provider.opts().parse_params(conf_params, cli_args)

# Create storage instance
with storage_provider.storage()(storage_opts) as storage:
    # Use storage
    devices = storage.make_devices(query)
```

## Device Management

### Creating Devices

```python
# Create devices from query
devices = storage.make_devices(
    query=query,
    preload_neighbors=True,
    use_mesh=False,
    preload_extra_fields=True
)

# Get single device
device = storage.get_device(device_id, preload_neighbors=True)
```

### Querying Devices

```python
# Resolve device IDs from query
device_ids = storage.resolve_object_ids_by_query(query)

# Resolve FQDNs from query
fqdns = storage.resolve_fdnds_by_query(query)

# Get all FQDNs
all_fqdns = storage.resolve_all_fdnds()
```

### Device Relationships

```python
# Search connections between devices
connections = storage.search_connections(device1, device2)

# Get neighbor information
neighbor_ids = device.neighbours_ids
neighbor_fqdns = device.neighbours_fqdns
```

## Interface Management

### Creating Interfaces

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
```

### Managing Interface Addresses

```python
# Add IP address to interface
interface.add_addr("192.168.1.1/24", vrf="default")

# Add address with VRF
interface.add_addr("10.0.0.1/24", vrf="management")
```

## Performance Management

### Performance Metrics

```python
# Flush performance metrics
storage.flush_perf()
```

## Storage Implementation Examples

### File-based Storage

```python
import json
from pathlib import Path
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
        
        # Simple string matching for example
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
        # Create and return Device object
        return self._create_device(obj_id, data)
    
    def _create_device(self, obj_id, data):
        # Implementation to create Device object
        pass
    
    def search_connections(self, device, neighbor):
        # Implementation to find connections
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

### Database Storage

```python
import sqlite3
from annet.storage import Storage, StorageProvider, StorageOpts

class DatabaseStorageOpts(StorageOpts):
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @classmethod
    def parse_params(cls, conf_params, cli_opts):
        return cls(conf_params.get("db_path", "inventory.db"))

class DatabaseStorage(Storage):
    def __init__(self, opts: DatabaseStorageOpts):
        self.opts = opts
        self.conn = sqlite3.connect(opts.db_path)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
    
    def resolve_object_ids_by_query(self, query):
        cursor = self.conn.cursor()
        if query.is_empty():
            cursor.execute("SELECT id FROM devices")
        else:
            cursor.execute("SELECT id FROM devices WHERE hostname LIKE ?", 
                          (f"%{query.query_string}%",))
        return [row[0] for row in cursor.fetchall()]
    
    # Implement other required methods...
```

## Configuration

### Storage Configuration

Storage providers are configured through the context system:

```yaml
# context.yml
storage:
  provider: "file"  # or "database", "api", etc.
  params:
    inventory_file: "/path/to/inventory.json"
    # or for database:
    # db_path: "/path/to/inventory.db"
    # host: "localhost"
    # port: 5432
```

### Environment Variables

- `ANN_STORAGE_PROVIDER`: Override storage provider
- `ANN_STORAGE_CONFIG`: Path to storage configuration

## Best Practices

### Storage Implementation

1. **Connection Management**: Always use context managers for connections
2. **Error Handling**: Implement proper error handling for data access
3. **Performance**: Consider caching and optimization for large inventories
4. **Thread Safety**: Ensure thread-safe operations if needed
5. **Resource Cleanup**: Always clean up resources in `__exit__`

### Device Implementation

1. **Immutability**: Consider making device objects immutable
2. **Lazy Loading**: Load expensive data only when needed
3. **Caching**: Cache frequently accessed data
4. **Validation**: Validate device data on creation

### Query Implementation

1. **Flexibility**: Support various query formats
2. **Performance**: Optimize query execution
3. **Error Handling**: Handle malformed queries gracefully
4. **Documentation**: Document supported query syntax

## Error Handling

### Common Exceptions

- `StorageError`: General storage-related errors
- `DeviceNotFoundError`: Device not found in storage
- `QueryError`: Invalid query format
- `ConnectionError`: Storage connection failed

### Error Handling Example

```python
from annet.storage import StorageError

try:
    devices = storage.make_devices(query)
except StorageError as e:
    logger.error(f"Storage error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise StorageError(f"Failed to create devices: {e}") from e
```