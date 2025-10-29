#!/usr/bin/env python3

"""
Webhook Receiver for CA Lobby Deployment Notifications
Handles Vercel deployment webhooks and triggers automated validation
Created: 2025-09-22
"""

import json
import hmac
import hashlib
import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/webhook_receiver.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class WebhookReceiver:
    """Handles incoming deployment webhooks and triggers validation"""

    def __init__(self):
        self.webhook_secret = self._load_webhook_secret()
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)

    def _load_webhook_secret(self) -> str:
        """Load webhook secret from file or environment"""
        secret_file = Path(".vercel-webhook-secret")

        if secret_file.exists():
            return secret_file.read_text().strip()

        secret = os.getenv("WEBHOOK_SECRET")
        if secret:
            return secret

        logger.warning("No webhook secret found - webhook validation disabled")
        return ""

    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature for security"""
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured - skipping signature verification")
            return True

        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        # Remove 'sha256=' prefix if present
        if signature.startswith('sha256='):
            signature = signature[7:]

        return hmac.compare_digest(expected_signature, signature)

    def parse_deployment_webhook(self, payload: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Parse Vercel deployment webhook payload"""
        try:
            deployment_info = {
                'url': payload.get('deployment', {}).get('url', ''),
                'state': payload.get('deployment', {}).get('state', ''),
                'type': payload.get('type', ''),
                'team': payload.get('team', {}).get('slug', ''),
                'project': payload.get('project', {}).get('name', ''),
                'timestamp': datetime.now().isoformat()
            }

            # Construct full URL if needed
            if deployment_info['url'] and not deployment_info['url'].startswith('http'):
                deployment_info['url'] = f"https://{deployment_info['url']}"

            return deployment_info

        except Exception as e:
            logger.error(f"Failed to parse webhook payload: {e}")
            return None

    def trigger_deployment_validation(self, deployment_url: str) -> bool:
        """Trigger automated deployment validation"""
        try:
            logger.info(f"Starting deployment validation for: {deployment_url}")

            # Run deployment validator script
            cmd = [
                './scripts/deployment-validator.sh',
                '--url', deployment_url,
                '--automated',
                '--webhook'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info("Deployment validation completed successfully")
                return True
            else:
                logger.error(f"Deployment validation failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Deployment validation timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to trigger deployment validation: {e}")
            return False

    def handle_deployment_webhook(self, payload: Dict[str, Any], signature: str = "") -> Dict[str, Any]:
        """Handle incoming deployment webhook"""

        # Verify signature if provided
        if signature and not self.verify_signature(json.dumps(payload), signature):
            logger.error("Invalid webhook signature")
            return {
                'status': 'error',
                'message': 'Invalid signature'
            }

        # Parse deployment information
        deployment_info = self.parse_deployment_webhook(payload)
        if not deployment_info:
            return {
                'status': 'error',
                'message': 'Invalid webhook payload'
            }

        logger.info(f"Received deployment webhook: {deployment_info}")

        # Only validate successful deployments
        if deployment_info['state'] == 'READY' and deployment_info['url']:

            # Trigger validation
            validation_success = self.trigger_deployment_validation(deployment_info['url'])

            # Log result
            result = {
                'status': 'success' if validation_success else 'failed',
                'deployment_url': deployment_info['url'],
                'validation_result': validation_success,
                'timestamp': deployment_info['timestamp']
            }

            # Save webhook result
            self._save_webhook_result(result)

            return result

        else:
            logger.info(f"Skipping validation for deployment state: {deployment_info['state']}")
            return {
                'status': 'skipped',
                'reason': f"Deployment state: {deployment_info['state']}",
                'deployment_url': deployment_info.get('url', 'unknown')
            }

    def _save_webhook_result(self, result: Dict[str, Any]) -> None:
        """Save webhook processing result to log file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = self.logs_dir / f"webhook_result_{timestamp}.json"

            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)

            logger.info(f"Webhook result saved to: {result_file}")

        except Exception as e:
            logger.error(f"Failed to save webhook result: {e}")

def simulate_deployment_webhook(deployment_url: str) -> None:
    """Simulate a deployment webhook for testing"""

    webhook_receiver = WebhookReceiver()

    # Create mock webhook payload
    mock_payload = {
        'type': 'deployment',
        'deployment': {
            'url': deployment_url,
            'state': 'READY'
        },
        'team': {
            'slug': 'test-team'
        },
        'project': {
            'name': 'ca-lobby-frontend'
        }
    }

    logger.info("Simulating deployment webhook...")
    result = webhook_receiver.handle_deployment_webhook(mock_payload)

    print("\n=== Webhook Simulation Result ===")
    print(json.dumps(result, indent=2))

def main():
    """Main function for testing webhook receiver"""
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            # Test mode with deployment URL
            deployment_url = sys.argv[2] if len(sys.argv) > 2 else "https://frontend-hx1b123f3-michaels-projects-73340e30.vercel.app"
            simulate_deployment_webhook(deployment_url)
        else:
            print("Usage: python webhook-receiver.py [--test] [deployment_url]")
    else:
        print("Webhook receiver initialized successfully")
        print("Use --test to simulate a webhook")

if __name__ == "__main__":
    main()