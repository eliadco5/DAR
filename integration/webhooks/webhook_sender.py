"""
Webhook notification system for Desktop Automation Recorder.
Provides integration with Slack, Discord, and custom HTTP endpoints.
"""

import json
import requests
import datetime
import os
import re
from urllib.parse import urlparse
from utils.logger import setup_logger

# Set up module logger
logger = setup_logger("WebhookSender")

class WebhookSender:
    """
    Sends webhook notifications to various services about test results.
    Supports Slack, Discord, and custom HTTP endpoints.
    """
    
    def __init__(self):
        """Initialize the webhook sender."""
        # Default headers for HTTP requests
        self.headers = {'Content-Type': 'application/json'}
    
    def _is_valid_url(self, url):
        """
        Check if the URL is valid.
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _detect_webhook_type(self, webhook_url):
        """
        Detect the type of webhook based on the URL.
        
        Args:
            webhook_url: Webhook URL
            
        Returns:
            str: 'slack', 'discord', or 'custom'
        """
        if 'hooks.slack.com' in webhook_url:
            return 'slack'
        elif 'discord.com/api/webhooks' in webhook_url:
            return 'discord'
        else:
            return 'custom'
    
    def send_notification(self, webhook_url, test_result, summary, title=None, custom_fields=None):
        """
        Send notification to a webhook URL.
        
        Args:
            webhook_url: Webhook URL
            test_result: 'success' or 'failure'
            summary: Summary text of the test result
            title: Optional title for the notification
            custom_fields: Optional dict of custom fields for the payload
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._is_valid_url(webhook_url):
            logger.error(f"Invalid webhook URL: {webhook_url}")
            return False
        
        webhook_type = self._detect_webhook_type(webhook_url)
        
        try:
            if webhook_type == 'slack':
                return self.send_slack_notification(webhook_url, test_result, summary, title, custom_fields)
            elif webhook_type == 'discord':
                return self.send_discord_notification(webhook_url, test_result, summary, title, custom_fields)
            else:
                return self.send_custom_notification(webhook_url, test_result, summary, title, custom_fields)
        except Exception as e:
            logger.error(f"Failed to send {webhook_type} notification: {e}")
            return False
    
    def send_slack_notification(self, webhook_url, test_result, summary, title=None, custom_fields=None):
        """
        Send notification to Slack.
        
        Args:
            webhook_url: Slack webhook URL
            test_result: 'success' or 'failure'
            summary: Summary text of the test result
            title: Optional title for the notification
            custom_fields: Optional dict of custom fields for the payload
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Determine color based on test result
        color = "#36a64f" if test_result == 'success' else "#ff0000"
        
        # Create the notification title
        notification_title = title or f"Test {'Succeeded' if test_result == 'success' else 'Failed'}"
        
        # Create the payload
        payload = {
            "text": notification_title,
            "attachments": [
                {
                    "color": color,
                    "title": notification_title,
                    "text": summary,
                    "fields": [],
                    "footer": "Desktop Automation Recorder",
                    "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                    "ts": int(datetime.datetime.now().timestamp())
                }
            ]
        }
        
        # Add custom fields if provided
        if custom_fields:
            for field_name, field_value in custom_fields.items():
                payload["attachments"][0]["fields"].append({
                    "title": field_name,
                    "value": field_value,
                    "short": len(str(field_value)) < 20
                })
        
        # Send the notification
        try:
            response = requests.post(webhook_url, json=payload, headers=self.headers)
            if response.status_code == 200:
                logger.info(f"Slack notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send Slack notification: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exception sending Slack notification: {e}")
            return False
    
    def send_discord_notification(self, webhook_url, test_result, summary, title=None, custom_fields=None):
        """
        Send notification to Discord.
        
        Args:
            webhook_url: Discord webhook URL
            test_result: 'success' or 'failure'
            summary: Summary text of the test result
            title: Optional title for the notification
            custom_fields: Optional dict of custom fields for the payload
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Determine color based on test result (Discord uses decimal color codes)
        color = 3066993 if test_result == 'success' else 15158332  # Green or Red
        
        # Create the notification title
        notification_title = title or f"Test {'Succeeded' if test_result == 'success' else 'Failed'}"
        
        # Create embed fields from custom fields
        fields = []
        if custom_fields:
            for field_name, field_value in custom_fields.items():
                fields.append({
                    "name": field_name,
                    "value": field_value,
                    "inline": len(str(field_value)) < 20
                })
        
        # Create the payload
        payload = {
            "content": notification_title,
            "embeds": [
                {
                    "title": notification_title,
                    "description": summary,
                    "color": color,
                    "fields": fields,
                    "footer": {
                        "text": f"Desktop Automation Recorder • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                }
            ]
        }
        
        # Send the notification
        try:
            response = requests.post(webhook_url, json=payload, headers=self.headers)
            if response.status_code == 204:  # Discord returns 204 No Content on success
                logger.info(f"Discord notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send Discord notification: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exception sending Discord notification: {e}")
            return False
    
    def send_custom_notification(self, webhook_url, test_result, summary, title=None, custom_fields=None):
        """
        Send notification to a custom HTTP endpoint.
        
        Args:
            webhook_url: Custom webhook URL
            test_result: 'success' or 'failure'
            summary: Summary text of the test result
            title: Optional title for the notification
            custom_fields: Optional dict of custom fields for the payload
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Create the notification title
        notification_title = title or f"Test {'Succeeded' if test_result == 'success' else 'Failed'}"
        
        # Create the payload
        payload = {
            "title": notification_title,
            "summary": summary,
            "result": test_result,
            "timestamp": datetime.datetime.now().isoformat(),
            "source": "Desktop Automation Recorder"
        }
        
        # Add custom fields if provided
        if custom_fields:
            payload["custom_fields"] = custom_fields
        
        # Send the notification
        try:
            response = requests.post(webhook_url, json=payload, headers=self.headers)
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Custom notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send custom notification: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exception sending custom notification: {e}")
            return False
    
    def send_test_result_notification(self, webhook_url, report_data, report_url=None):
        """
        Send a comprehensive test result notification based on report data.
        
        Args:
            webhook_url: Webhook URL
            report_data: Report data dictionary
            report_url: Optional URL to the HTML report
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Determine test result
        test_result = 'success' if report_data['failed_actions'] == 0 else 'failure'
        
        # Create summary text
        summary = (
            f"Test run completed with {report_data['successful_actions']} successful "
            f"and {report_data['failed_actions']} failed actions. "
            f"Total duration: {report_data['duration']:.2f} seconds."
        )
        
        # Create custom fields
        custom_fields = {
            "Total Actions": report_data['total_actions'],
            "Successful": report_data['successful_actions'],
            "Failed": report_data['failed_actions'],
            "Duration": f"{report_data['duration']:.2f} seconds",
            "OS": report_data['environment']['platform'],
            "Resolution": report_data['environment']['resolution']
        }
        
        # Add report URL if available
        if report_url:
            custom_fields["Report URL"] = report_url
        
        # Create title
        title = f"Test Run {report_data['timestamp']} - {'Succeeded' if test_result == 'success' else 'Failed'}"
        
        # Send notification
        return self.send_notification(webhook_url, test_result, summary, title, custom_fields) 