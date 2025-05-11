# Changelog

## [Unreleased]

### Added
- Added new `utils/logger.py` module for centralized logging configuration
- Added proper logger setup and configuration
- Added comprehensive integration capabilities:
  - CI/CD integration for running tests in automated environments
  - Report generation in HTML, PDF, and JSON formats with screenshots
  - Webhook notifications to Slack, Discord, and custom HTTP endpoints
- Added GitHub Actions workflow for automated testing
- Added example scripts demonstrating integration features

### Changed
- Moved all test files from the root directory to the `tests/` directory
- Replaced all `print` statements with proper logger calls 
- Updated README.md with more detailed project structure information
- Improved code organization and structure
- Enhanced requirements.txt with new dependencies (jinja2, requests)

### Fixed
- Fixed inconsistent logging throughout the application
- Improved error handling with better logging 