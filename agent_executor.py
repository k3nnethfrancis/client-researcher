"""
Agent Workflow Executor

This script executes the main agent workflow, including content research and report generation.
It can be run ad-hoc or scheduled to run periodically.

Usage:
    python agent.py --client <client_name> [--context <additional_context>]

Options:
    --client    Name of the client (required)
    --context   Additional context to guide the search (optional)
"""

import argparse
import logging
import json
import os
from datetime import datetime
from typing import Dict, List

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from agents.content_researcher import research_content, ContentResearcherResults
from agents.client_profiler import ClientProfile

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_client_profile(client_name: str) -> ClientProfile:
    """Load a client profile from the profiles directory."""
    filename = f"profiles/{client_name.replace(' ', '_').lower()}.json"
    if not os.path.exists(filename):
        raise FileNotFoundError(f"No profile found for {client_name}. Please run the client profiler first.")
    
    with open(filename, 'r') as f:
        profile_data = json.load(f)
    return ClientProfile(**profile_data)

def generate_report(research_results: ContentResearcherResults, client_profile: ClientProfile, additional_context: str = "") -> str:
    """Generate a markdown report based on the research results and client profile."""
    report_generator = Agent(
        name="Report Generator",
        role="Generate insightful reports based on research results",
        model=OpenAIChat(id="gpt-4"),
    )

    prompt = f"""
    Generate a markdown report for our client based on the following information:

    Client Profile:
    {json.dumps(client_profile.dict(), indent=2)}

    Research Results:
    {json.dumps(research_results.dict(), indent=2)}

    Additional Context:
    {additional_context}

    The report should include:
    1. A brief summary of the most relevant and interesting findings
    2. How these findings relate to the client's expertise and goals
    3. Any actionable insights or recommendations
    4. A section highlighting the most relevant news or developments in the client's industry

    Format the report in markdown, with appropriate headers, bullet points, and emphasis where needed.
    """

    response = report_generator.run(prompt)
    return response.content

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

    # Load client profile
    client_profile = load_client_profile(client_name)

    # Perform content research
    research_results = research_content(client_profile.dict(), additional_context)

    # Generate report
    report = generate_report(research_results, client_profile, additional_context)

    # Save report
    save_report(report, client_name)

    logger.info("Agent workflow completed successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute the agent workflow for a client.")
    parser.add_argument("--client", required=True, help="Name of the client")
    parser.add_argument("--context", default="", help="Additional context to guide the search")
    
    args = parser.parse_args()
    
    main(args.client, args.context)
