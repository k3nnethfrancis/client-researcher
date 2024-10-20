"""
Agent Workflow Executor

This script executes the main agent workflow, including content research and report generation.
It can be run ad-hoc or scheduled to run periodically.

Usage:
    python agent_executor.py --client <client_name> [--context <additional_context>]

Options:
    --client    Name of the client (required)
    --context   Additional context to guide the search (optional)
"""

import argparse
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any

from agents.client_profiler import ClientProfile, main as run_client_profiler
from agents.content_researcher import research_content, ContentResearcherResults
from agents.report_generator import generate_report

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_client_profile(client_name: str, context: str = "") -> ClientProfile:
    """Load a client profile from the profiles directory or create a new one if it doesn't exist."""
    filename = f"profiles/{client_name.replace(' ', '_').lower()}.json"
    if not os.path.exists(filename):
        logger.info(f"No profile found for {client_name}. Running client profiler.")
        try:
            profile = run_client_profiler(client_name, context)
            logger.info(f"Profile generated successfully for {client_name}")
            return profile
        except Exception as e:
            logger.error(f"Failed to create profile for {client_name}: {str(e)}")
            raise
    
    logger.info(f"Loading profile from {filename}")
    with open(filename, 'r') as f:
        profile_data = json.load(f)
    return ClientProfile(**profile_data)

def save_report(report: str, client_name: str):
    """Save the generated report as a markdown file."""
    os.makedirs('reports', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/{client_name.replace(' ', '_').lower()}_{timestamp}.md"
    with open(filename, 'w') as f:
        f.write(report)
    logger.info(f"Report saved to {filename}")

def main(client_name: str, additional_context: str = ""):
    """Execute the main agent workflow."""
    logger.info(f"Starting agent workflow for client: {client_name}")

    # Load or create client profile
    client_profile = load_client_profile(client_name, additional_context)
    logger.info(f"Loaded profile for {client_name}")

    # Perform content research
    research_results = research_content(client_profile.dict(), additional_context)
    logger.info("Content research completed")

    # Generate report
    report = generate_report(research_results, client_profile, additional_context)
    logger.info("Report generated")

    # Save report
    save_report(report, client_name)

    logger.info("Agent workflow completed successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute the agent workflow for a client.")
    parser.add_argument("--client", required=True, help="Name of the client")
    parser.add_argument("--context", default="", help="Additional context to guide the search")
    
    args = parser.parse_args()
    
    main(args.client, args.context)
