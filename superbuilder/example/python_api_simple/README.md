# SuperBuilder Python gRPC Client API

A sample Python client library for interacting with Intel AI Assistant Builder (SuperBuilder) via gRPC. This client provides easy-to-use functions to check status, manage models, download installers, and configure the SuperBuilder service.

## Overview

This client demonstrates how to:
- Connect to SuperBuilder gRPC service
- Check system and service status
- Manage LLM models and configurations
- Download models and installers
- Monitor chat and RAG readiness

## Prerequisites

- Python 3.8 or higher
- Intel AI Assistant Builder (SuperBuilder) running locally
- SuperBuilder gRPC service accessible at `localhost:5006`

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
   - Windows (CMD): `.venv\Scripts\activate.bat`
   - Linux/Mac: `source .venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Dependencies

- `grpcio` - gRPC runtime for Python
- `grpcio-tools` - Protocol buffer compiler tools
- `protobuf` - Protocol buffer support
- `tqdm` - Progress bar for downloads

## Project Structure

```
python-chatPPT/
├── api.py                              # Main API implementation
├── utils.py                            # Utility functions and gRPC helpers
├── requirements.txt                    # Python dependencies
├── superbuilder_service_pb2.py        # Generated protobuf messages
├── superbuilder_service_pb2_grpc.py   # Generated gRPC stubs
└── README.md                          # This file
```

## Configuration

Default configuration in `utils.py`:

```python
GRPC_ADDRESS = 'localhost:5006'
DEFAULT_MODEL_PATH = "C:\\ProgramData\\IntelAIA\\local_models"
DEFAULT_LLM = 'Qwen3-8B-int4-ov'
DEFAULT_EMBEDDER = 'bge-base-en-v1.5-int8-ov'
DEFAULT_RANKER = 'bge-reranker-base-int8-ov'
```

## API Functions

### Connection Management

#### `aab_init()`
Initialize connection to SuperBuilder service.

**Returns:** `(success, stub, channel)` tuple

**Example:**
```python
success, stub, channel = aab_init()
if success:
    print("Connected to SuperBuilder")
```

#### `utils.disconnect(stub, channel)`
Disconnect from SuperBuilder service.

### Status Checking

#### `superbuilder_status(stub)`
Check SuperBuilder middleware service status.

**Returns:** JSON string with system information (CPU, GPU, memory, NPU)

#### `llm_status(stub)`
Check LLM backend service status.

**Returns:** Status message or False if service unavailable

#### `assistant_status(stub)`
Get active assistant configuration.

**Returns:** Dictionary with assistant name and model configuration

### Model Management

#### `set_models(stub, model_path)`
Load LLM, embedder, and ranker models from specified path.

**Parameters:**
- `model_path`: Path to model directory

**Returns:** Response from SetModels gRPC call

### Download Functions

#### `download_installer(stub)`
Download latest SuperBuilder installer from Intel web portal.

**Default URL:** `https://aibuilder.intel.com/installers/...`

**Default Path:** `C:\temp\Intel_AI_Assistant_Builder_Installer.exe`

#### `utils.download(stub, url, local_path)`
Download files with progress bar.

**Parameters:**
- `url`: File URL to download
- `local_path`: Local destination path

### Configuration

#### `utils.get_config(stub)`
Get current client configuration.

**Returns:** Dictionary with configuration data

#### `utils.set_config(stub, assistant, config_data)`
Set active assistant configuration.

**Parameters:**
- `assistant`: Assistant name
- `config_data`: JSON configuration string

## Usage Example

### Basic Usage

```python
import utils
from api import *

# Initialize connection
success, stub, channel = aab_init()

if not success:
    print("Failed to connect to SuperBuilder")
    exit(1)

try:
    # Check SuperBuilder status
    status = superbuilder_status(stub)
    print(f"SuperBuilder Status: {status}")
    
    # Check LLM status
    llm = llm_status(stub)
    print(f"LLM Status: {llm}")
    
    # Get assistant configuration
    assistant = assistant_status(stub)
    print(f"Active Assistant: {assistant}")
    
    # Load models
    set_models(stub, utils.DEFAULT_MODEL_PATH)
    
finally:
    # Always disconnect
    utils.disconnect(stub, channel)
```

### Running the Demo

Simply run the main script:

```bash
python api.py
```

This will execute all demo functions and display:
- SuperBuilder system status
- LLM backend status
- Chat and RAG readiness
- Model status
- Active assistant configuration

## API Feature Map

| Feature | Chinese | Status | Function |
|---------|---------|--------|----------|
| Download | 下载SuperBuilder | ✅ | `download_installer()` |
| SilentInstall | 静态安装 | 🚧 TBD | `silent_install()` |
| SilentUninstall | - | 🚧 TBD | `silent_uninstall()` |
| SilentUpdate | 静态更新 | 🚧 TBD | `silent_update()` |
| SuperBuilderStatus | 当前的SuperBuilder状态 | ✅ | `superbuilder_status()` |
| VersionEnable | 版本更新信息 | ✅ | `get_software_update()` |
| ChatEnable | 开启对话 | ✅ | `llm_status()` |
| RagEnable | 开启RAG功能 | ✅ | `llm_status()` |
DownloadModel | 下载模型 | ✅ | `download_model()` |
| LoadModel | 加载模型 | ✅ | `set_models()` |
| ModelStatus | 模型状态 | ✅ | `assistant_status()` |

## Troubleshooting

### Connection Failed
**Error:** "gRPC channel connection busy or missing"

**Solution:**
- Ensure SuperBuilder is running
- Check if port 5006 is accessible
- Verify firewall settings

### JSON Parse Error
**Error:** "Expecting value: line 1 column 1 (char 0)"

**Solution:**
- Service may be returning empty response
- Check if SuperBuilder backend is properly initialized
- Verify models are loaded

### Model Not Found
**Error:** "Models not found"

**Solution:**
- Check `DEFAULT_MODEL_PATH` exists
- Verify model files are downloaded:
  - `Qwen3-8B-int4-ov`
  - `bge-base-en-v1.5-int8-ov`
  - `bge-reranker-base-int8-ov`

## Protobuf Files

The `.proto` definition file is located at:
```
../../proto/superbuilder_service.proto
```

To regenerate protobuf files:
```bash
python -m grpc_tools.protoc -I../../proto --python_out=. --grpc_python_out=. ../../proto/superbuilder_service.proto
```
