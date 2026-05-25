# Getting Started with VALDPY

## Installation

### Prerequisites
- Python 3.8 or higher
- pip or conda package manager

### Install from PyPI (Coming Soon)
```bash
pip install valdpy
```

### Install from Source
```bash
git clone https://github.com/dgaytanjenkins/Valdpy.git
cd Valdpy
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/dgaytanjenkins/Valdpy.git
cd Valdpy
pip install -e ".[dev]"
```

## Setting Up Credentials

### Step 1: Get VALD API Credentials
1. Contact VALD Support to obtain API access
2. Receive your `client_id`, `client_secret`, and `tenant_id`

### Step 2: Create Credentials File
Create a file named `vald_api_cred.txt` in your project directory:

```json
{
    "client_id": "your_client_id_here",
    "client_secret": "your_client_secret_here",
    "tenant_id": "your_tenant_id_here"
}
```

**⚠️ Security Warning:** 
- Never commit credentials to version control
- Add `vald_api_cred.txt` to `.gitignore`
- Consider using environment variables for production

### Step 3: Load Credentials
```python
from valdpy.utils import read_credentials

creds = read_credentials('vald_api_cred.txt')
print(f"Loaded credentials for tenant: {creds['tenant_id']}")
```

## Basic Usage

### Initialize Authentication
```python
from valdpy import ValdAuth

auth = ValdAuth(
    client_id='your_client_id',
    client_secret='your_client_secret',
    tenant_id='your_tenant_id',
    region='USA'  # or 'Australia' or 'Europe'
)

# Get access token
auth.get_token()
print(f"Token obtained: {auth.token[:20]}...")
```

### Access Test Data
```python
from valdpy import ForeDecksAPI

# Initialize ForceDecks API
fd = ForeDecksAPI(
    tenant_id=auth.tenant_id,
    header=auth.header,
    region='USA'
)

# Get tests from January 1, 2025
tests_df = fd.get_tests_info('01/01/2025')
print(f"Found {len(tests_df)} tests")
print(tests_df.head())
```

### Process Results
```python
# Get results for the first test
test_id = tests_df['id'].iloc[0]
results_json, definitions = fd.get_test_results(test_id)

# Get raw force trace data
force_trace = fd.get_force_trace(test_id)
print(force_trace.head())

# Export to CSV
force_trace.to_csv('force_data.csv', index=False)
```

## Next Steps

- See [Quick Start Guide](quick_start.md) for more examples
- Read [API Reference](api_reference/) for detailed documentation
- Check [Examples](../examples/) for Jupyter notebooks
