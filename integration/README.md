# Integration Capabilities for Desktop Automation Recorder

This module provides integration capabilities for the Desktop Automation Recorder, allowing it to be used in CI/CD environments, generate comprehensive reports, and send notifications.

## Features

### 1. CI/CD Integration

Run tests in automated environments like GitHub Actions, Jenkins, and GitLab CI:

```bash
# Basic usage
python -m integration.ci.ci_runner path/to/test_script.py

# With options
python -m integration.ci.ci_runner path/to/test_script.py --headless --report html --timeout 300
```

Options:
- `--headless`: Run in headless mode
- `--report`: Report format ('html', 'pdf', 'json', or 'all')
- `--timeout`: Maximum execution time in seconds
- `--retries`: Number of retries if the test fails
- `--retry-delay`: Delay between retries in seconds
- `--open-report`: Open the report after generation
- `--webhook`: Webhook URL for notifications

### 2. Report Generation

Generate detailed HTML, PDF, and JSON reports with screenshots and metrics:

```python
from integration.reports.report_generator import ReportGenerator

# Create a report generator
report_gen = ReportGenerator()

# Record actions
for action in actions:
    report_gen.record_action(action, success=True)

# Generate reports
html_path = report_gen.generate_html_report()
pdf_path = report_gen.generate_pdf_report()
json_path = report_gen.generate_json_report()

# Open the report
report_gen.open_report()
```

### 3. Webhook Notifications

Send notifications to Slack, Discord, or custom HTTP endpoints:

```python
from integration.webhooks.webhook_sender import WebhookSender

# Create a webhook sender
webhook = WebhookSender()

# Send notification
webhook.send_notification(
    "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXX", 
    test_result="success", 
    summary="Test completed successfully"
)

# Send test results with custom fields
webhook.send_test_result_notification(
    "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXX",
    report_data,
    report_url="https://example.com/reports/report.html"
)
```

## Directory Structure

- `ci/`: CI/CD integration functionality
- `reports/`: Report generation functionality
- `webhooks/`: Webhook notification functionality

## Requirements

The integration capabilities require the following dependencies:
- `jinja2`: For HTML report templates
- `requests`: For webhook notifications
- `weasyprint` (optional): For PDF report generation 