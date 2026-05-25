# VALDPY Examples

This directory contains Jupyter notebook examples demonstrating how to use VALDPY with each VALD Performance platform.

## 📓 Examples Included

### [Vald_forceDecks_Example.ipynb](Vald_forceDecks_Example.ipynb)
**Force plate testing** - Demonstrates ForceDecks API usage for retrieving and analyzing force production data.

**Key Methods:**
- `get_tests_info()` - Retrieve tests from a specific date
- `get_test_results()` - Get force metrics for a test
- `get_force_trace()` - Raw force-time data

### [Vald_Dynamo_Example.ipynb](Vald_Dynamo_Example.ipynb)
**Jump and power testing** - Shows how to access Dynamo jump data with force-velocity metrics.

**Key Methods:**
- `get_tests()` - Get tests within a date range
- `get_test_results()` - Retrieve power output metrics

### [Vald_forceFrame_Example.ipynb](Vald_forceFrame_Example.ipynb)
**Advanced force measurement** - Demonstrates ForceFrame API for detailed biomechanical data.

**Key Methods:**
- `get_tests_info()` - Query tests by date
- `get_test_results()` - Access force metrics

### [Vald_Nordbord_Example.ipynb](Vald_Nordbord_Example.ipynb)
**Leg press strength** - Examples using NordBord API for lower body strength assessment.

**Key Methods:**
- `get_tests_info()` - Get strength test data
- `get_test_results()` - Force and position metrics

### [Vald_Smartspeed_Example.ipynb](Vald_Smartspeed_Example.ipynb)
**Timing gate system** - Shows SmartSpeed API usage for sprint and agility data.

**Key Methods:**
- `get_tests_info()` - Retrieve timing gate tests
- `get_test_results()` - Sprint/acceleration metrics

## 🚀 Getting Started

### 1. Install VALDPY
```bash
pip install -e ..
```

### 2. Setup Credentials
Create a `vald_api_cred.txt` file in your working directory (or the same directory as the notebook):

```json
{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "tenant_id": "your_tenant_id"
}
```

**⚠️ IMPORTANT:**
- Never commit `vald_api_cred.txt` to GitHub
- Add it to your `.gitignore`
- Keep credentials secure and never share them

### 3. Run a Notebook
Open any notebook and follow the examples to:
1. Load credentials
2. Initialize authentication
3. Connect to API endpoints
4. Retrieve and analyze test data

## 📊 Data Analysis Workflow

Each example follows this pattern:

```python
from valdpy import ValdAuth, ForeDecksAPI
from valdpy.utils import read_credentials

# Load credentials
creds = read_credentials('vald_api_cred.txt')

# Authenticate
auth = ValdAuth(**creds)
auth.get_token()

# Initialize API client
fd = ForeDecksAPI(auth.tenant_id, auth.header)

# Retrieve data
tests = fd.get_tests_info('01/01/2025')

# Export to CSV
tests.to_csv('forcedecks_tests.csv', index=False)
```

## 💡 Tips

- **Date Formats**: Use 'dd/mm/yyyy' or datetime objects
- **Large Datasets**: The API supports pagination - check status codes
- **Pandas**: Results are returned as DataFrames for easy analysis
- **Regional Endpoints**: Specify `region` parameter for USA, Australia, or Europe

## 📝 Common Tasks

### Filter by Date Range
```python
tests = dynamo.get_tests('01/01/2025', '31/01/2025')
```

### Filter by Profile
```python
tests = fd.get_tests_info('01/01/2025', profile_id='PROFILE_ID')
```

### Combine Multiple Tests
```python
all_results = []
for test_id in tests['id'].head(10):
    results = fd.get_test_results(test_id)
    all_results.append(results)

import pandas as pd
combined = pd.concat(all_results)
```

### Export Data
```python
tests.to_csv('tests.csv', index=False)
tests.to_excel('tests.xlsx', index=False)
tests.to_json('tests.json')
```

## 🔗 Resources

- [VALDPY Documentation](../README.md)
- [VALD API Docs](https://support.vald.com/hc/en-au/articles/23415335574553-How-to-integrate-with-VALD-APIs)
- [Getting Started Guide](../docs/getting_started.md)

## ❓ Troubleshooting

### ImportError
```
ModuleNotFoundError: No module named 'valdpy'
```
**Solution:** Install the package with `pip install -e ..` from the examples directory

### Authentication Error
```
Failed to obtain token. Status Code: 401
```
**Solution:** 
- Verify credentials in `vald_api_cred.txt`
- Check that credentials are still valid
- Ensure you're using the correct region

### No Data Found
- Verify the date range is correct
- Check that tenant_id has tests on that date
- Ensure profile_id (if specified) has data

## 📬 Support

- Check [Getting Started Guide](../docs/getting_started.md)
- Review [CONTRIBUTING.md](../CONTRIBUTING.md)
- Open an [Issue](https://github.com/dgaytanjenkins/Valdpy/issues)

---

Happy analyzing! 📈
