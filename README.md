# VALDpy - Python Tools for VALD Performance APIs

A comprehensive Python wrapper for **VALD Performance** APIs, providing easy access to data from ForceDecks, Dynamo, ForceFrame, NordBord, and SmartSpeed testing platforms.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-yellow)

## Overview

VALDPY simplifies integration with VALD Performance's test data APIs. Whether you're analyzing jump performance, force production, sprint times, or strength metrics, this SDK provides a clean, Pythonic interface for authentication, data retrieval, and processing.

Built on the [VALD API Documentation](https://support.vald.com/hc/en-au/articles/23415335574553-How-to-integrate-with-VALD-APIs), this package handles:
- OAuth 2.0 authentication
- Multi-region API access (USA, Australia, Europe)
- Test data retrieval across all VALD platforms
- Automatic pagination for large datasets
- Data parsing into pandas DataFrames

## Installation

### From PyPI (Recommended)
```bash
pip install valdpy
```

Available on [PyPI](https://pypi.org/project/valdpy/).

### From Source
```bash
git clone https://github.com/dgaytanjenkins/Valdpy.git
cd Valdpy
pip install -e .
```

### Development Installation
```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Setup Credentials

Create a JSON credentials file (`vald_api_cred.txt`):
```json
{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "tenant_id": "your_tenant_id"
}
```

### 2. Basic Usage

```python
from valdpy import ValdAuth, ForeDecksAPI
from valdpy.utils import read_credentials

# Load credentials
creds = read_credentials('vald_api_cred.txt')

# Initialize authentication
auth = ValdAuth(
    client_id=creds['client_id'],
    client_secret=creds['client_secret'],
    tenant_id=creds['tenant_id'],
    region='USA'
)

# Get access token
auth.get_token()

# Initialize ForceDecks API
fd = ForeDecksAPI(
    tenant_id=auth.tenant_id,
    header=auth.header,
    region='USA'
)

# Retrieve tests from a specific date
tests_df = fd.get_tests_info('01/01/2025')
print(tests_df.head())

# Get results for a specific test
test_id = tests_df['id'].iloc[0]
results_df = fd.get_test_results(test_id)
```

## Supported Platforms

### ForceDecks
Force plate testing for power, landing mechanics, and injury risk assessment.

```python
from valdpy import ForeDecksAPI

fd = ForeDecksAPI(tenant_id, header, region='USA')
tests_df = fd.get_tests_info('01/01/2025')
results_df = fd.get_test_results(test_id)
force_trace = fd.get_force_trace(test_id)  # Raw force data
recording_details = fd.get_recording_details(test_id)
```

### Dynamo
Jump and power testing platform for assessing lower body power production.

```python
from valdpy import DynamoAPI

dynamo = DynamoAPI(tenant_id, header)
tests_df = dynamo.get_tests('01/01/2025', '31/01/2025')
results_df = dynamo.get_test_results(test_id)
```

### ForceFrame
Advanced force measurement system for detailed biomechanical analysis.

```python
from valdpy import ForceFrameAPI

ff = ForceFrameAPI(tenant_id, header)
tests_df = ff.get_tests_info('01/01/2025')
results_df = ff.get_test_results(test_id)
```

### NordBord
Leg press strength testing platform for lower body strength assessment.

```python
from valdpy import NordBordAPI

nb = NordBordAPI(tenant_id, header)
tests_df = nb.get_tests_info('01/01/2025')
results_df = nb.get_test_results(test_id)
```

### SmartSpeed
Timing gate system for sprint, agility, and acceleration testing.

```python
from valdpy import SmartSpeedAPI

ss = SmartSpeedAPI(tenant_id, header)
tests_df = ss.get_tests_info('01/01/2025')
results_df = ss.get_test_results(test_id)
```

## API Reference

### ValdAuth
Main authentication class for VALD APIs.

**Methods:**
- `get_token()` - Obtain OAuth 2.0 access token
- `get_all_tenants()` - List all accessible tenants
- `get_tenant_info(tenant_id)` - Get specific tenant details
- `get_tenant_categories()` - List categories (e.g., Team, Injured)
- `get_tenant_groups()` - List all groups in tenant
- `get_group_profiles(group_name, category_name)` - List profiles in a group
- `assign_groups(profile_id, group_ids)` - Assign groups to a profile

### Utility Functions
Located in `valdpy.utils`:

- `read_credentials(filepath)` - Load credentials from JSON file
- `convert_ticks_to_datetime(ticks)` - Convert .NET ticks to datetime
- `format_date_to_iso8601(date)` - Format datetime to ISO 8601
- `get_call()` - Make GET requests to API
- `post_call()` - Make POST requests to API
- `put_call()` - Make PUT requests to API

## Examples

Complete example notebooks are available in the `examples/` directory:

- [ForceDecks Example](examples/Vald_forceDecks_Example.ipynb)
- [Dynamo Example](examples/Vald_Dynamo_Example.ipynb)
- [ForceFrame Example](examples/Vald_forceFrame_Example.ipynb)
- [NordBord Example](examples/Vald_Nordbord_Example.ipynb)
- [SmartSpeed Example](examples/Vald_Smartspeed_Example.ipynb)

## Data Processing Examples

### Filter tests by date range
```python
from datetime import datetime
import pandas as pd

# Get tests for January 2025
start = '01/01/2025'
end = '31/01/2025'
tests_df = dynamo.get_tests(start, end)

# Filter by specific profile
specific_profile = tests_df[tests_df['profileId'] == 'profile_123']
```

### Combine results across multiple tests
```python
all_results = []

for test_id in tests_df['id'].head(10):
    results = fd.get_test_results(test_id)
    all_results.append(results)

combined_df = pd.concat(all_results, ignore_index=True)
```

### Export to CSV
```python
tests_df.to_csv('forcedecks_tests.csv', index=False)
results_df.to_csv('test_results.csv', index=False)
```

## Regional Endpoints

VALDPY supports three regional endpoints:

- **USA**: Primary US endpoint
- **Australia**: AU/NZ endpoint
- **Europe**: European endpoint

Specify region when initializing clients:

```python
auth = ValdAuth(..., region='Australia')
fd = ForeDecksAPI(..., region='Europe')
```

## Configuration

Environment variables can override defaults:

```bash
export VALD_REGION=USA
export VALD_CREDENTIALS_PATH=/path/to/credentials.json
```

## Testing

Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=valdpy
```

## Development

### Project Structure
```
valdpy/
├── api/                    # API client implementations
│   ├── __init__.py
│   ├── auth.py            # Authentication
│   ├── dynamo.py          # Dynamo API
│   ├── forcedecks.py      # ForceDecks API
│   ├── forceframe.py      # ForceFrame API
│   ├── nordbord.py        # NordBord API
│   └── smartspeed.py      # SmartSpeed API
├── utils.py               # Utility functions
└── __init__.py            # Package initialization

examples/                  # Jupyter notebook examples
docs/                      # Documentation
tests/                     # Test suite
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **MyPy** for type checking
- **Flake8** for linting

Run formatters:
```bash
black valdpy/
isort valdpy/
```

## Documentation

Full API documentation is available in [docs/](docs/).

### Building Documentation Locally
```bash
pip install -e ".[docs]"
cd docs
make html
open _build/html/index.html
```

## Troubleshooting

### Authentication Fails
- Verify credentials in `vald_api_cred.txt`
- Check that client credentials have appropriate permissions
- Ensure credentials are valid and not expired

### No Data Returned
- Verify date range (max 180 days for some endpoints)
- Check that tenant_id and profile_id are correct
- Ensure modified dates are in ISO 8601 format

### Network Errors
- Verify API region is correct
- Check internet connectivity
- Review VALD API status page

## Changelog

### Version 0.1.0 (2025-05-25)
- Initial release
- Support for all five VALD platforms
- OAuth 2.0 authentication
- Multi-region support
- Pandas DataFrame outputs

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Citation

If you use VALDPY in your research, please cite:

```bibtex
@software{gaytan_jenkins_2025_valdpy,
  title={VALDPY: Python SDK for VALD Performance APIs},
  author={Gaytan-Jenkins, Danny},
  year={2025},
  url={https://github.com/dgaytanjenkins/Valdpy}
}
```

## Support

- 📖 [VALD API Documentation](https://support.vald.com/hc/en-au/articles/23415335574553-How-to-integrate-with-VALD-APIs)
- 🐛 [Report Issues](https://github.com/dgaytanjenkins/Valdpy/issues)
- 💬 [Discussions](https://github.com/dgaytanjenkins/Valdpy/discussions)

## Disclaimer

This package is provided as-is and is not officially affiliated with VALD Performance. Users are responsible for complying with VALD's API terms of service and any applicable licensing agreements.

---

**Built by:** Danny Gaytan-Jenkins  
**Email:** dgaytanj@uoregon.edu  
**Last Updated:** May 25, 2025
