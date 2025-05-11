"""
Example script demonstrating how to use the report generation capabilities
of the Desktop Automation Recorder.
"""

import os
import sys
import time
from PIL import Image, ImageDraw, ImageChops
import pyautogui

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from integration.reports.report_generator import ReportGenerator
from integration.webhooks.webhook_sender import WebhookSender

def create_sample_image(width, height, text, color=(255, 255, 255), bg_color=(50, 50, 50)):
    """Create a sample image with text."""
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    text_width = draw.textlength(text)
    text_x = (width - text_width) / 2
    text_y = height / 2 - 10
    draw.text((text_x, text_y), text, fill=color)
    return img

def main():
    # Create a report generator
    report_gen = ReportGenerator(output_dir="example_reports")
    
    # Set environment info
    screen_width, screen_height = pyautogui.size()
    report_gen.set_environment_info(f"{screen_width}x{screen_height}")
    
    # Simulate some actions
    
    # 1. Mouse movement
    mouse_action = {
        'type': 'mouse',
        'event': 'move',
        'x': 100,
        'y': 100,
        'timestamp': time.time()
    }
    # Take a screenshot
    mouse_screenshot = create_sample_image(200, 200, "Mouse Move")
    report_gen.record_action(mouse_action, success=True, screenshot=mouse_screenshot)
    
    # 2. Keyboard action
    keyboard_action = {
        'type': 'keyboard',
        'event': 'down',
        'key': 'a',
        'timestamp': time.time()
    }
    keyboard_screenshot = create_sample_image(200, 200, "Keyboard Press")
    report_gen.record_action(keyboard_action, success=True, screenshot=keyboard_screenshot)
    
    # 3. Failed action
    failed_action = {
        'type': 'mouse',
        'event': 'down',
        'x': 200,
        'y': 200,
        'timestamp': time.time()
    }
    failed_screenshot = create_sample_image(200, 200, "Failed Action", color=(255, 0, 0))
    report_gen.record_action(
        failed_action, 
        success=False, 
        screenshot=failed_screenshot,
        error_message="Element not found at coordinates (200, 200)"
    )
    
    # 4. Visual check
    check_action = {
        'type': 'check',
        'check_type': 'image',
        'check_name': 'Sample Check',
        'image': create_sample_image(300, 200, "Reference Image"),
        'timestamp': time.time()
    }
    report_gen.record_action(check_action, success=True)
    
    # 5. Failed visual check
    failed_check_action = {
        'type': 'check',
        'check_type': 'image',
        'check_name': 'Failed Check',
        'image': create_sample_image(300, 200, "Another Reference"),
        'timestamp': time.time()
    }
    report_gen.record_action(failed_check_action, success=False, error_message="Images do not match")
    
    # Create check result with actual image
    reference_img = create_sample_image(300, 200, "Another Reference")
    actual_img = create_sample_image(300, 200, "Actual Image", bg_color=(70, 50, 50))
    
    # Create diff image
    diff_img = ImageChops.difference(reference_img, actual_img)
    
    # Record check result
    report_gen.record_check_result(
        check_index=1,  # Second check (0-indexed)
        success=False,
        actual_image=actual_img,
        diff_image=diff_img,
        error_message="Images differ by 15% (threshold: 10%)"
    )
    
    # 6. Comment action
    comment_action = {
        'type': 'comment',
        'comment': 'This is a sample comment',
        'timestamp': time.time()
    }
    report_gen.record_action(comment_action, success=True)
    
    # Generate reports
    html_path = report_gen.generate_html_report()
    json_path = report_gen.generate_json_report()
    pdf_path = report_gen.generate_pdf_report()
    
    print(f"HTML report generated: {html_path}")
    print(f"JSON report generated: {json_path}")
    if pdf_path:
        print(f"PDF report generated: {pdf_path}")
    else:
        print("PDF report not generated (WeasyPrint not installed)")
    
    # Open the report
    report_gen.open_report()
    
    # Optional: Send webhook notification
    if len(sys.argv) > 1 and sys.argv[1].startswith('http'):
        webhook_url = sys.argv[1]
        print(f"Sending notification to: {webhook_url}")
        
        webhook = WebhookSender()
        success = webhook.send_test_result_notification(
            webhook_url,
            report_gen.report_data
        )
        
        if success:
            print("Notification sent successfully")
        else:
            print("Failed to send notification")

if __name__ == '__main__':
    # Create the directory structure if it doesn't exist
    os.makedirs("integration/examples", exist_ok=True)
    
    # Run the example
    main() 