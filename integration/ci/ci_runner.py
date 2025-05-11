"""
CI/CD integration for Desktop Automation Recorder.
Allows running tests in automated environments like GitHub Actions, Jenkins, or GitLab CI.
"""

import os
import sys
import json
import argparse
import datetime
import importlib.util
import traceback
import pyautogui
import time
from utils.logger import setup_logger
from integration.reports.report_generator import ReportGenerator
from integration.webhooks.webhook_sender import WebhookSender

# Set up module logger
logger = setup_logger("CIRunner")

class CIRunner:
    """
    Runs automation tests in CI/CD environments.
    Provides command-line interface and integrates with reporting and notification systems.
    """
    
    def __init__(self):
        """Initialize the CI runner."""
        self.report_generator = ReportGenerator()
        self.webhook_sender = WebhookSender()
        self.current_script = None
        self.exit_code = 0
        
        # Configure PyAutoGUI for CI environments
        pyautogui.FAILSAFE = False  # Disable failsafe in CI
    
    def _load_script(self, script_path):
        """
        Load a Python script as a module.
        
        Args:
            script_path: Path to the Python script
            
        Returns:
            module: Loaded Python module or None if failed
        """
        try:
            # Create a unique module name based on the file path
            module_name = f"dar_ci_script_{os.path.basename(script_path).replace('.', '_')}"
            
            # Create the module spec
            spec = importlib.util.spec_from_file_location(module_name, script_path)
            if spec is None:
                logger.error(f"Could not load module spec from {script_path}")
                return None
                
            # Create the module
            module = importlib.util.module_from_spec(spec)
            
            # Add the module to sys.modules
            sys.modules[module_name] = module
            
            # Execute the module
            spec.loader.exec_module(module)
            
            return module
        except Exception as e:
            logger.error(f"Failed to load script {script_path}: {e}")
            traceback.print_exc()
            return None
    
    def _configure_environment(self, headless=False):
        """
        Configure the environment for CI/CD.
        
        Args:
            headless: Whether to run in headless mode
        """
        # Set CI environment variables
        os.environ["DAR_CI_MODE"] = "1"
        
        # Configure for headless mode if needed
        if headless:
            os.environ["DAR_HEADLESS"] = "1"
            logger.info("Running in headless mode")
            
            # Additional headless configuration could go here
            # e.g., configuring a virtual framebuffer like Xvfb
        
        # Disable system prompts and notifications
        os.environ["DAR_NO_PROMPTS"] = "1"
        
        # Set the default screenshot directory for CI
        if not os.environ.get("DAR_SCREENSHOT_DIR"):
            os.environ["DAR_SCREENSHOT_DIR"] = os.path.join(os.getcwd(), "ci_screenshots")
            os.makedirs(os.environ["DAR_SCREENSHOT_DIR"], exist_ok=True)
    
    def _detect_ci_environment(self):
        """
        Detect CI environment based on environment variables.
        
        Returns:
            str: Name of CI environment or None if not detected
        """
        if os.environ.get("GITHUB_ACTIONS"):
            return "GitHub Actions"
        elif os.environ.get("GITLAB_CI"):
            return "GitLab CI"
        elif os.environ.get("JENKINS_URL"):
            return "Jenkins"
        elif os.environ.get("TRAVIS"):
            return "Travis CI"
        elif os.environ.get("CIRCLECI"):
            return "CircleCI"
        elif os.environ.get("APPVEYOR"):
            return "AppVeyor"
        elif os.environ.get("AZURE_DEVOPS"):
            return "Azure DevOps"
        else:
            return None
    
    def run_test_script(self, script_path, timeout=300, retries=1, retry_delay=5, headless=False):
        """
        Run a test script in CI/CD environment.
        
        Args:
            script_path: Path to the test script
            timeout: Maximum execution time in seconds
            retries: Number of retries if the test fails
            retry_delay: Delay between retries in seconds
            headless: Whether to run in headless mode
            
        Returns:
            bool: True if the test succeeded, False otherwise
        """
        self.current_script = script_path
        success = False
        attempt = 0
        
        # Configure the environment
        self._configure_environment(headless)
        
        # Record the screen resolution
        screen_width, screen_height = pyautogui.size()
        self.report_generator.set_environment_info(f"{screen_width}x{screen_height}")
        
        # Detect CI environment
        ci_env = self._detect_ci_environment()
        if ci_env:
            logger.info(f"Detected CI environment: {ci_env}")
        
        # Set up the report
        script_name = os.path.basename(script_path)
        logger.info(f"Running test script: {script_name}")
        
        while attempt < retries:
            attempt += 1
            logger.info(f"Attempt {attempt}/{retries}")
            
            try:
                # Clear any existing actions or screenshots from previous attempts
                if os.environ.get("DAR_SCREENSHOT_DIR") and os.path.exists(os.environ["DAR_SCREENSHOT_DIR"]):
                    for file in os.listdir(os.environ["DAR_SCREENSHOT_DIR"]):
                        if file.endswith(".png"):
                            os.remove(os.path.join(os.environ["DAR_SCREENSHOT_DIR"], file))
                
                # Load the script
                module = self._load_script(script_path)
                if not module:
                    if attempt < retries:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        self.exit_code = 1
                        return False
                
                # Check if the module has a main function
                if hasattr(module, "main"):
                    # Execute with timeout
                    import threading
                    import queue
                    
                    result_queue = queue.Queue()
                    
                    def execute_test():
                        try:
                            module.main()
                            result_queue.put(True)
                        except Exception as e:
                            logger.error(f"Test execution failed: {e}")
                            traceback.print_exc()
                            result_queue.put(False)
                    
                    # Start the test in a separate thread
                    test_thread = threading.Thread(target=execute_test)
                    test_thread.daemon = True
                    test_thread.start()
                    
                    # Wait for the test to complete with timeout
                    try:
                        success = result_queue.get(timeout=timeout)
                        if success:
                            logger.info("Test execution succeeded")
                            break
                        else:
                            logger.error("Test execution failed")
                    except queue.Empty:
                        logger.error(f"Test execution timed out after {timeout} seconds")
                        success = False
                else:
                    # Just execute the script directly
                    try:
                        success = True
                        logger.info("Script executed without errors")
                        break
                    except Exception as e:
                        logger.error(f"Script execution failed: {e}")
                        traceback.print_exc()
                        success = False
            except Exception as e:
                logger.error(f"Unexpected error running test: {e}")
                traceback.print_exc()
                success = False
            
            if not success and attempt < retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        
        # Set exit code
        self.exit_code = 0 if success else 1
        
        return success
    
    def generate_reports(self, format='html', open_report=False):
        """
        Generate reports after test execution.
        
        Args:
            format: Report format ('html', 'pdf', 'json', or 'all')
            open_report: Whether to open the report after generation
            
        Returns:
            dict: Paths to generated reports
        """
        reports = {}
        
        try:
            if format.lower() == 'html' or format.lower() == 'all':
                html_path = self.report_generator.generate_html_report()
                if html_path:
                    reports['html'] = html_path
                    logger.info(f"HTML report generated: {html_path}")
            
            if format.lower() == 'pdf' or format.lower() == 'all':
                pdf_path = self.report_generator.generate_pdf_report()
                if pdf_path:
                    reports['pdf'] = pdf_path
                    logger.info(f"PDF report generated: {pdf_path}")
            
            if format.lower() == 'json' or format.lower() == 'all':
                json_path = self.report_generator.generate_json_report()
                if json_path:
                    reports['json'] = json_path
                    logger.info(f"JSON report generated: {json_path}")
            
            if open_report and 'html' in reports:
                self.report_generator.open_report(reports['html'])
        except Exception as e:
            logger.error(f"Failed to generate reports: {e}")
            traceback.print_exc()
        
        return reports
    
    def send_notifications(self, webhook_urls):
        """
        Send notifications to webhook URLs after test execution.
        
        Args:
            webhook_urls: List of webhook URLs or comma-separated string
            
        Returns:
            bool: True if all notifications were sent successfully, False otherwise
        """
        if not webhook_urls:
            return True
        
        # Convert string to list if needed
        if isinstance(webhook_urls, str):
            webhook_urls = [url.strip() for url in webhook_urls.split(',')]
        
        all_success = True
        
        # Send notifications to all webhook URLs
        for webhook_url in webhook_urls:
            if not webhook_url:
                continue
                
            try:
                success = self.webhook_sender.send_test_result_notification(
                    webhook_url, 
                    self.report_generator.report_data
                )
                if not success:
                    all_success = False
            except Exception as e:
                logger.error(f"Failed to send notification to {webhook_url}: {e}")
                all_success = False
        
        return all_success
    
    def parse_args(self):
        """
        Parse command-line arguments.
        
        Returns:
            argparse.Namespace: Parsed arguments
        """
        parser = argparse.ArgumentParser(description='Run Desktop Automation Recorder tests in CI/CD environments')
        parser.add_argument('script', help='Path to the test script to run')
        parser.add_argument('--timeout', type=int, default=300, help='Maximum execution time in seconds')
        parser.add_argument('--retries', type=int, default=1, help='Number of retries if the test fails')
        parser.add_argument('--retry-delay', type=int, default=5, help='Delay between retries in seconds')
        parser.add_argument('--headless', action='store_true', help='Run in headless mode')
        parser.add_argument('--report', choices=['html', 'pdf', 'json', 'all'], default='html', help='Report format')
        parser.add_argument('--open-report', action='store_true', help='Open the report after generation')
        parser.add_argument('--webhook', help='Webhook URL to send notifications (comma-separated for multiple)')
        
        return parser.parse_args()
    
    def main(self):
        """
        Main entry point for the CI runner.
        
        Returns:
            int: Exit code (0 for success, non-zero for failure)
        """
        args = self.parse_args()
        
        # Run the test script
        success = self.run_test_script(
            args.script,
            timeout=args.timeout,
            retries=args.retries,
            retry_delay=args.retry_delay,
            headless=args.headless
        )
        
        # Generate reports
        reports = self.generate_reports(args.report, args.open_report)
        
        # Send notifications if webhook URLs are provided
        if args.webhook:
            self.send_notifications(args.webhook)
        
        return self.exit_code

# Run the CI runner if this script is executed directly
if __name__ == '__main__':
    ci_runner = CIRunner()
    sys.exit(ci_runner.main()) 