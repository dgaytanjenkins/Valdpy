# Changelog

All notable changes to VALDPY will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Support for all five VALD testing platforms
- OAuth 2.0 authentication with token management
- Multi-region API support (USA, Australia, Europe)
- Automatic pagination for large datasets
- Type hints for better IDE support
- Comprehensive documentation and examples

### Changed
- Refactored original API utilities into modular classes
- Improved error handling and status code management

### Fixed
- Fixed date formatting for API requests
- Improved credentials file handling

## [0.1.0] - 2025-05-25

### Added
- Initial release
- **ValdAuth**: Authentication and tenant management
- **ForeDecksAPI**: Force plate testing data access
- **DynamoAPI**: Jump and power testing data access
- **ForceFrameAPI**: Advanced force measurement data access
- **NordBordAPI**: Leg press strength testing data access
- **SmartSpeedAPI**: Timing gate system data access
- Utility functions for API interactions
- Pandas DataFrame outputs for easy data analysis
- Jupyter notebook examples for each platform
- Comprehensive documentation
- MIT License

### Known Limitations
- Currently read-only for test data retrieval
- Profile assignments require additional development
- Real-time data streaming not yet supported

---

## Version History

### v0.1.0 (Initial Release)
- First stable release with full support for VALD APIs

---

For older versions and more details, see [GitHub Releases](https://github.com/dgaytanjenkins/Valdpy/releases)
