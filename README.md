# Desktop Automation Recorder

A user-friendly desktop application to record and replay user interactions for automation and testing, using Python and PyAutoGUI.

## Features
- Record mouse and keyboard actions
- Element-based and image-based recording
- Edit, save, and replay sessions
- Export to runnable Python scripts
- Generate comprehensive HTML, PDF and JSON reports
- CI/CD integration for automated testing
- Webhook notifications to Slack, Discord, or custom endpoints

## Limitations
- **System/global shortcuts (e.g., ALT+TAB, WIN+R):**
  - These may be recorded, but cannot be reliably replayed due to operating system restrictions. PyAutoGUI and similar libraries cannot trigger system-level shortcuts during playback.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```

## Project Structure
The project is organized into the following directories:
- `gui/`: User interface components
- `recorder/`: Recording functionality
- `playback/`: Action playback and execution
- `scriptgen/`: Script generation
- `storage/`: Saving and loading sessions
- `utils/`: Utility functions and helpers
- `tests/`: Test files and test cases
- `integration/`: CI/CD integration, reporting, and notifications

## Integration Capabilities

### CI/CD Integration

Run tests in automated environments like GitHub Actions:

```bash
python -m integration.ci.ci_runner tests/test_full_functionality.py --report html
```

For more details, see [Integration README](integration/README.md).

### Report Generation

Generate detailed reports with screenshots and metrics:

```python
from integration.reports.report_generator import ReportGenerator

report_gen = ReportGenerator()
# Record test actions...
html_path = report_gen.generate_html_report()
```

### Webhook Notifications

Send notifications to Slack, Discord, or custom HTTP endpoints:

```python
from integration.webhooks.webhook_sender import WebhookSender

webhook = WebhookSender()
webhook.send_notification(
    "https://hooks.slack.com/services/XXX/YYY/ZZZ", 
    test_result="success", 
    summary="Test completed successfully"
)
```

## Testing
To run the tests, use the following command:
```bash
python -m tests.run_tests
```

Or run individual test files:
```bash
python -m tests.test_name
```

See the `tests/README.md` file for more information on the testing framework. 